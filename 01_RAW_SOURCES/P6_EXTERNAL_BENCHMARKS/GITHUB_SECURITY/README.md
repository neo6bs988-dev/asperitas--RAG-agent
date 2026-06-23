# GITHUB_SECURITY Benchmark Notes

Priority: P6 External Benchmark
Use: CI, branch protection, dependency review, static analysis, release discipline.

## Sources
1. GitHub Actions docs
   - URL: https://docs.github.com/en/actions
2. GitHub Code Security docs
   - URL: https://docs.github.com/en/code-security

## Patterns to Absorb
- CI should run tests, linting, artifact verification, and eval smoke tests.
- Branch protection should prevent unreviewed risky changes to main.
- Dependency review and static analysis should catch supply-chain and code-risk regressions.
- Release notes should summarize tests, eval deltas, risks, and rollback instructions.

## Asperitas V1 Application
- Add GitHub Actions after MVP-016/017 stabilizes local test commands.
- Keep main recoverable.
- Prefer small PRs with clear objective, tests, metrics, risks, and next action.
