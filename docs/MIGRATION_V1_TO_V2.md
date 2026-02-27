# Migration Guide: v1 to v2

## What Changed

### Configuration: `.cursorrules` -> `CLAUDE.md`

v1 used `.cursorrules` for AI configuration. v2 uses `CLAUDE.md`, which works with both Claude Code and Cursor IDE.

**Action:** Your `.cursorrules` file still works in Cursor IDE. For Claude Code, rename it to `CLAUDE.md` or copy the new `CLAUDE.md` from this repo.

### New config fields in CLAUDE.md

```
SKILLS_REPO:   # Path to claude-skills repo (optional)
```

### Documentation language

All docs are now in English. The v1 `docs/WORKFLOW.md` had mixed Ukrainian/English content.

### Priority formula alignment

The `age_factor` cap in `scripts/calculate_priority.py` is now `min(0.3, ...)` to match the documented formula. In v1, the script used `min(1.0, ...)` which could over-weight task age.

### Ecosystem references

v2 introduces references to two companion repos:
- [plaintext-crm](https://github.com/anthroos/plaintext-crm) -- CRM (unchanged)
- [claude-skills](https://github.com/anthroos/claude-skills) -- Skills framework, agents, automation (new)

### CRM integration directory structure

The CRM `relationships/` folder now includes `partners.csv` alongside `leads.csv`, `clients.csv`, and `deals.csv`.

## Data Migration

**No data migration needed.** The CSV schema is unchanged. Your existing `pm/` data files work with v2 without modification.

## Steps

1. Pull the latest v2 from the repo
2. Copy the new `CLAUDE.md` to your project root
3. Edit `CLAUDE.md`: set your name, enable CRM integration if needed
4. Delete `.cursorrules` (or keep it if you also use Cursor IDE)
5. Run `python3 scripts/validate_pm.py` to verify your data
