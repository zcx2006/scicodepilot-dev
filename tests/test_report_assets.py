from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_doc(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_final_report_draft_exists_and_states_scope() -> None:
    text = read_doc("docs/final_report_draft.md")

    assert "not a public benchmark" in text
    assert "not a SOTA comparison" in text


def test_report_claims_checklist_contains_allowed_and_disallowed_claims() -> None:
    text = read_doc("docs/report_claims_checklist.md")

    assert "Allowed Claims" in text
    assert "Disallowed Claims" in text
    assert "SciCodePilot evaluates a structured failure-memory pipeline" in text
    assert "SciCodePilot achieves SOTA" in text


def test_table_and_figure_inventory_lists_core_assets() -> None:
    text = read_doc("docs/table_and_figure_inventory.md")

    assert "ablation_table.md" in text
    assert "system_pipeline.md" in text


def test_demo_story_mentions_reproducibility_and_public_extension() -> None:
    text = read_doc("docs/demo_story.md")

    assert "reproducibility manifest" in text
    assert "public benchmark extension" in text


def test_final_report_draft_avoids_false_claims() -> None:
    text = read_doc("docs/final_report_draft.md")
    forbidden_claims = [
        "state-of-the-art",
        "outperforms SWE-agent",
        "completed SWE-bench",
        "completed BugsInPy",
    ]

    for claim in forbidden_claims:
        assert claim not in text
