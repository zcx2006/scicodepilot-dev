# Three Cases Claims Checklist

## Safe To Say

- We validated three BugsInPy-derived external repair patterns.
- Case 001 remained `patch_success` after the three-case backend extension.
- Case 002 is no longer `unsupported_external_failure` for the conservative `str_to_int` TypeError pattern.
- Case 003 is no longer `unsupported_external_failure` for the conservative command-level `unified_strdate(... ) is None` assertion pattern.
- Patches are applied only in isolated workspaces.
- Summaries record `original_repo_mutated: false`.
- The real WSL repo paths for Case 002 and Case 003 were unavailable, so minimal local external repos were used for verification in this environment.

## Do Not Say

- We completed the BugsInPy benchmark.
- We achieved SOTA.
- We can repair arbitrary GitHub repositories.
- External smoke equals benchmark performance.
- All external TypeErrors or AssertionErrors are supported.
- Case 002 and Case 003 were rerun against the original external repos in WSL.

## Suggested Wording

Use: "three BugsInPy-derived external repair patterns validated, with Case 001 rerun on an existing external workspace copy and Case 002/003 verified on minimal local external repos."
