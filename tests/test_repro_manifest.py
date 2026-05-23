from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_export_repro_manifest_module():
    script_path = PROJECT_ROOT / "scripts" / "export_repro_manifest.py"
    spec = importlib.util.spec_from_file_location("export_repro_manifest", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_export_repro_manifest_generates_manifest_for_bundle_dir(tmp_path, monkeypatch):
    module = load_export_repro_manifest_module()
    bundle_dir = tmp_path / "repro_bundle" / "20260523_195337"
    bundle_dir.mkdir(parents=True)

    (bundle_dir / "git_commit.txt").write_text("abc123\n", encoding="utf-8")
    (bundle_dir / "git_status.txt").write_text("", encoding="utf-8")
    (bundle_dir / "python_version.txt").write_text("Python 3.11.0\n", encoding="utf-8")
    (bundle_dir / "env.from_history.yml").write_text("name: scicodepilot-dev\n", encoding="utf-8")
    (bundle_dir / "env.explicit.txt").write_text("@EXPLICIT\n", encoding="utf-8")
    (bundle_dir / "pip_freeze.txt").write_text("pytest==8.0.0\n", encoding="utf-8")

    report_manifest = tmp_path / "report_assets" / "tables" / "repro_bundle_manifest.md"
    monkeypatch.setattr(module, "REPORT_MANIFEST_PATH", report_manifest)

    output_path, bundle_manifest_path, missing_files = module.export_manifest(bundle_dir)

    assert output_path == report_manifest
    assert output_path.exists()
    assert bundle_manifest_path == bundle_dir / "manifest.md"
    assert bundle_manifest_path.exists()
    assert "gpu_info.csv" in missing_files
    assert "docker_version.txt" in missing_files

    manifest_text = output_path.read_text(encoding="utf-8")
    assert "Reproducibility Bundle Manifest" in manifest_text
    assert "abc123" in manifest_text
    assert "Git status clean: `yes`" in manifest_text
    assert "`gpu_info.csv`" in manifest_text
    assert "internal controlled experiments" in manifest_text


def test_reproducibility_doc_contains_key_commands():
    text = (PROJECT_ROOT / "docs" / "reproducibility.md").read_text(encoding="utf-8")

    assert "pytest -q" in text
    assert "python scripts/run_experiments.py --mode diagnosis" in text
    assert "python scripts/run_experiments.py --mode repair" in text
    assert "python scripts/run_experiments.py --mode repair --confirm-apply" in text
    assert "python scripts/run_ablation_experiments.py --quick --include-safety" in text
    assert "python scripts/export_ablation_tables.py --latest" in text
    assert "python scripts/export_repro_manifest.py" in text


def test_internal_ablation_v2_scope_statement():
    text = (PROJECT_ROOT / "docs" / "internal_ablation_v2.md").read_text(encoding="utf-8")

    assert "Internal Controlled Ablation Study" in text
    assert "not a public benchmark" in text
