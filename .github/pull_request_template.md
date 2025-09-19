## Summary
- What changed? Why?

## Issue / Context (optional)
- Link to discussion or problem statement

## Test Plan
- [ ] Unit tests pass (`pytest`)
- [ ] Local curl against /healthz
- [ ] Local sample PDFs analyzed as expected

## Screens / Logs (optional)
- Paste short logs or screenshots if helpful

## Risk & Rollout
- [ ] No DB migrations OR migrations are backward-compatible
- [ ] No breaking API changes OR versioned properly
- Post-merge: verify staging auto-deploys from `main`

## Checklist
- [ ] Updated `CHANGELOG.md` (Unreleased)
- [ ] Follows Conventional Commits (`feat:`, `fix:`, etc.)
- [ ] Code reviewed (PR checks green)