# V1.0.0-rc1 Manual Release Steps

Status: reference commands only

These commands are for manual, human-approved release creation after review. Do not run tag or GitHub release commands from automation.

Fresh command output from this manual context is required before publishing release notes, making any GO claim, creating `v1.0.0-rc1`, starting an internal dry-run, or claiming internal release.

## Verification Commands

```bash
git checkout main
git pull --ff-only origin main
python -m pytest -q
python scripts/verify_artifacts.py
python scripts/check_v1_release_readiness.py --json
python scripts/run_v1_rc_smoke.py --json
python scripts/ask_asperitas_agent.py --question "What is Asperitas RAG Agent?" --json
```

## Human-Approved Only

```bash
git tag -a v1.0.0-rc1 -m "Asperitas AI RAG Agent v1.0.0-rc1 internal release candidate"
git push origin v1.0.0-rc1
```

## Optional GitHub CLI, Human-Approved Only

```bash
gh release create v1.0.0-rc1 --title "v1.0.0-rc1 internal RC" --notes-file docs/releases/V1_0_0_RC1_RELEASE_NOTES.md --prerelease --draft
```

## Boundaries

Do not create tags or releases until the full internal closeout packet passes and a human explicitly approves the tag/release action.
