from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from scicodepilot.memory.record import FailureMemoryRecord, RetrievedFailureMemory


TOKEN_PATTERN = re.compile(r"[a-z0-9_./-]+")
PATH_TOKEN_PATTERN = re.compile(r"[a-z0-9_./-]*[/._-][a-z0-9_./-]*")


def tokenize(text: str | None) -> set[str]:
    """Tokenize text into lowercase alphanumeric/path-like tokens."""

    if not text:
        return set()
    return set(TOKEN_PATTERN.findall(text.lower()))


def record_text(record: FailureMemoryRecord) -> str:
    parts: list[str] = []
    for value in record.to_dict().values():
        if isinstance(value, dict):
            parts.extend(str(item) for pair in value.items() for item in pair)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
        elif value is not None:
            parts.append(str(value))
    return " ".join(parts)


def query_text(query: FailureMemoryRecord | str) -> str:
    if isinstance(query, FailureMemoryRecord):
        return record_text(query)
    return query


class FailureMemoryStore:
    """JSONL-backed deterministic failure memory store."""

    def __init__(self, records: Iterable[FailureMemoryRecord] | None = None) -> None:
        self._records = list(records or [])

    @classmethod
    def load_jsonl(cls, path: str | Path) -> "FailureMemoryStore":
        jsonl_path = Path(path)
        if not jsonl_path.exists():
            return cls()

        records: list[FailureMemoryRecord] = []
        with jsonl_path.open("r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Malformed JSONL row at line {line_number}: {exc.msg}"
                    ) from exc
                if not isinstance(data, dict):
                    raise ValueError(
                        f"Malformed JSONL row at line {line_number}: expected object"
                    )
                try:
                    records.append(FailureMemoryRecord.from_dict(data))
                except ValueError as exc:
                    raise ValueError(
                        f"Malformed JSONL row at line {line_number}: {exc}"
                    ) from exc
        return cls(records)

    def save_jsonl(self, path: str | Path) -> None:
        jsonl_path = Path(path)
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with jsonl_path.open("w", encoding="utf-8") as file:
            for record in self._records:
                file.write(json.dumps(record.to_dict(), ensure_ascii=False, sort_keys=True))
                file.write("\n")

    def append(self, record: FailureMemoryRecord) -> None:
        self._records.append(record)

    def all_records(self) -> list[FailureMemoryRecord]:
        return list(self._records)

    def retrieve(
        self,
        query: FailureMemoryRecord | str,
        top_k: int = 3,
    ) -> list[RetrievedFailureMemory]:
        if top_k <= 0 or not self._records:
            return []

        query_tokens = tokenize(query_text(query))
        query_error_type = query.error_type if isinstance(query, FailureMemoryRecord) else None
        query_exception_type = (
            query.exception_type if isinstance(query, FailureMemoryRecord) else None
        )
        query_path_tokens = {
            token for token in query_tokens if PATH_TOKEN_PATTERN.fullmatch(token)
        }

        retrieved: list[RetrievedFailureMemory] = []
        for record in self._records:
            current_tokens = tokenize(record_text(record))
            matched_terms = sorted(query_tokens & current_tokens)
            score = self._score(
                query_tokens=query_tokens,
                record_tokens=current_tokens,
                matched_terms=matched_terms,
                query_error_type=query_error_type,
                query_exception_type=query_exception_type,
                record=record,
                query_path_tokens=query_path_tokens,
            )
            retrieved.append(
                RetrievedFailureMemory(
                    record=record,
                    score=round(score, 6),
                    matched_terms=matched_terms,
                )
            )

        return sorted(
            retrieved,
            key=lambda item: (-item.score, item.record.record_id),
        )[:top_k]

    def _score(
        self,
        query_tokens: set[str],
        record_tokens: set[str],
        matched_terms: list[str],
        query_error_type: str | None,
        query_exception_type: str | None,
        record: FailureMemoryRecord,
        query_path_tokens: set[str],
    ) -> float:
        if not query_tokens or not record_tokens:
            base_score = 0.0
        else:
            base_score = len(matched_terms) / len(query_tokens | record_tokens)

        score = base_score
        if query_error_type and query_error_type == record.error_type:
            score += 1.0
        if query_exception_type and query_exception_type == record.exception_type:
            score += 0.5

        record_path_tokens = {
            token for token in record_tokens if PATH_TOKEN_PATTERN.fullmatch(token)
        }
        if query_path_tokens & record_path_tokens:
            score += 0.2
        return score
