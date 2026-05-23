#!/usr/bin/env python3
"""Export a Markdown manifest for the latest reproducibility bundle."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE_ROOT = PROJECT_ROOT / "artifacts" / "repro_bundle"
REPORT_MANIFEST_PATH = PROJECT_ROOT / "report_assets" / "tables" / "repro_bundle_manifest.md"

EXPECTED_FILES = (
    "git_commit.txt",
    "git_status.txt",
    "python_version.txt",
    "uname.txt",
    "env.from_history.yml",
    "env.explicit.txt",
    "pip_freeze.txt",
    "gpu_info.csv",
    "docker_version.txt",
    "docker_images.txt",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a Markdown manifest for a SciCodePilot repro bundle."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=None,
        help="Repro bundle directory. Defaults to the newest artifacts/repro_bundle/* directory.",
    )
    return parser.parse_args()


def latest_bundle_dir(bundle_root: Path = DEFAULT_BUNDLE_ROOT) -> Path:
    if not bundle_root.exists():
        raise FileNotFoundError(f"Bundle root does not exist: {bundle_root}")

    candidates = sorted(
        (path for path in bundle_root.iterdir() if path.is_dir()),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"No repro bundle directories found under: {bundle_root}")
    return candidates[0]


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def file_status_rows(bundle_dir: Path, expected_files: Iterable[str]) -> list[str]:
    rows = ["| File | Status |", "| --- | --- |"]
    for name in expected_files:
        status = "present" if (bundle_dir / name).exists() else "missing"
        rows.append(f"| `{name}` | {status} |")
    return rows


def git_status_is_clean(git_status_text: str, git_status_exists: bool) -> str:
    if not git_status_exists:
        return "unknown (git_status.txt missing)"
    return "yes" if not git_status_text.strip() else "no"


def build_manifest(bundle_dir: Path, inspected_at: datetime | None = None) -> tuple[str, list[str]]:
    inspected_at = inspected_at or datetime.now().astimezone()
    bundle_dir = bundle_dir.resolve()

    missing_files = [name for name in EXPECTED_FILES if not (bundle_dir / name).exists()]
    git_commit = first_nonempty_line(read_text(bundle_dir / "git_commit.txt")) or "missing"
    git_status_text = read_text(bundle_dir / "git_status.txt")
    python_version = first_nonempty_line(read_text(bundle_dir / "python_version.txt")) or "missing"

    conda_env_files_present = all(
        (bundle_dir / name).exists() for name in ("env.from_history.yml", "env.explicit.txt")
    )
    pip_freeze_present = (bundle_dir / "pip_freeze.txt").exists()
    gpu_info_present = (bundle_dir / "gpu_info.csv").exists()
    docker_info_present = all(
        (bundle_dir / name).exists() for name in ("docker_version.txt", "docker_images.txt")
    )

    lines = [
        "# Reproducibility Bundle Manifest",
        "",
        f"- Bundle path: `{bundle_dir}`",
        f"- Inspected time: `{inspected_at.isoformat(timespec='seconds')}`",
        f"- Git commit: `{git_commit}`",
        f"- Git status clean: `{git_status_is_clean(git_status_text, (bundle_dir / 'git_status.txt').exists())}`",
        f"- Python version: `{python_version}`",
        f"- Conda environment files present: `{str(conda_env_files_present).lower()}`",
        f"- pip freeze present: `{str(pip_freeze_present).lower()}`",
        f"- GPU info present: `{str(gpu_info_present).lower()}`",
        f"- Docker info present: `{str(docker_info_present).lower()}`",
        "",
        "## Expected Files",
        "",
        *file_status_rows(bundle_dir, EXPECTED_FILES),
        "",
        "## Missing Files",
        "",
    ]

    if missing_files:
        lines.extend(f"- `{name}`" for name in missing_files)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            (
                "This bundle freezes the source revision, Python environment, package list, "
                "system metadata, and optional hardware/container metadata used for "
                "SciCodePilot internal controlled experiments."
            ),
            (
                "The manifest is an inspection record for reproducibility assets. Missing "
                "optional files are reported here instead of causing export failure."
            ),
        ]
    )

    return "\n".join(lines) + "\n", missing_files


def export_manifest(bundle_dir: Path) -> tuple[Path, Path, list[str]]:
    manifest, missing_files = build_manifest(bundle_dir)
    REPORT_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MANIFEST_PATH.write_text(manifest, encoding="utf-8")

    bundle_manifest_path = bundle_dir / "manifest.md"
    bundle_manifest_path.write_text(manifest, encoding="utf-8")
    return REPORT_MANIFEST_PATH, bundle_manifest_path, missing_files


def main() -> int:
    args = parse_args()
    bundle_dir = args.bundle_dir.resolve() if args.bundle_dir else latest_bundle_dir()
    report_path, bundle_path, missing_files = export_manifest(bundle_dir)

    print(f"Wrote report manifest: {report_path}")
    print(f"Wrote bundle manifest: {bundle_path}")
    if missing_files:
        print("Missing files: " + ", ".join(missing_files))
    else:
        print("Missing files: none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
