# Patch Safety Cases

PatchSafetyReviewer is evaluated with static cases in
`tests/test_patch_safety_reviewer.py`. It does not execute shell commands and
does not modify files.

## Blocked Cases

- absolute path target files
- `../` path traversal
- `benchmark/` path modification
- `outputs/` path modification
- `tests/` path modification
- `reference/` path modification
- `.git/` path modification
- `requirements.txt` modification
- `pyproject.toml` modification
- `pip install` or `conda install` in a diff
- `rm -rf`
- `sudo`
- `os.system`, `subprocess`, `eval`, or `exec`
- multi-file diff

## Warning Cases

Weak alignment between the parsed error type and patch content should raise
medium risk and warning text, but it does not necessarily block the patch.

## Evaluation Use

For the research report, these safety cases support the claim that
PatchSafetyReviewer can catch dangerous or out-of-bound patches before
PatchApprovalRequired or PatchApplied.
