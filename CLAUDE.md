# CLAUDE.md

This file governs work across **every repository under `MoleculeID/repos/`** (VeroMass marketing site, the app backend/frontend, utility scripts, and the VOLTA desktop app). It is read from this parent directory regardless of which specific repo a session is working in. Repo-specific facts are in the **Repository Map** section at the bottom — read that before touching a given repo, since the policy sections above it are deliberately generic.

# Engineering Operating Standards

You are working on a production application.

Your responsibility is not only to write code, but to deliver reliable, maintainable, tested, and production-ready changes.

Every task must include appropriate planning, implementation, validation, testing, regression review, and risk assessment.

---

# Primary Objectives

Always prioritize:

1. Correctness
2. Reliability
3. Security
4. Data Integrity
5. Maintainability
6. Performance
7. User Experience

Never sacrifice existing functionality to implement a new feature.

When requirements are unclear, ask questions before making assumptions.

---

# High-Impact Change Review

Before making changes that could affect critical systems, perform an impact review.

Pay special attention to changes involving:

- Authentication
- Authorization
- User permissions
- Payments
- Billing
- Subscription logic
- User data
- Personal information
- Database schema
- Data migrations
- Production infrastructure
- Deployment processes
- External integrations
- Security controls
- Application availability

For high-impact changes:

1. Explain the potential impact.
2. Identify affected systems or components.
3. Identify risks.
4. Describe mitigation steps.
5. Confirm the implementation approach if the risk is significant.

Do not make assumptions about critical systems.

Prefer:

- Reversible changes
- Safe migrations
- Backward-compatible changes
- Rollback plans
- Incremental releases

Avoid destructive operations.

---

# Change Risk Classification

Classify changes before implementation.

## Low Risk

Examples:

- Documentation updates
- Copy changes
- Styling changes
- Minor UI adjustments

Proceed normally with appropriate validation.

## Medium Risk

Examples:

- New features
- API changes
- Database queries
- New dependencies
- Significant refactoring

Perform additional review and testing.

## High Risk

Examples:

- Authentication changes
- Authorization changes
- Payments
- Billing
- Database migrations
- User data changes
- Production infrastructure

Require impact analysis, testing strategy, and rollback considerations.

**The Final Response Format below scales with this classification.** Low-risk changes get a brief summary, not all 8 sections — see the note at the top of that section.

---

# Development Workflow

Before writing code:

- Review the relevant files.
- Understand the current architecture.
- Identify affected components.
- Review existing patterns.
- Explain the implementation approach for significant changes.

Do not immediately code without understanding the existing system.

Keep changes focused.

Do not refactor unrelated code unless explicitly requested.

**Git safety, specific to this multi-repo setup:** before committing in any of these repos, check `git status` and current branch — a repo can have another in-progress branch or unmerged work sitting on it (this has happened here before: `moleculeid-api` had an unmerged `feature/pay-per-run-matching` branch mid-session). If the working branch isn't `main`, stash, switch to `main`, and reapply rather than committing onto an unrelated branch. Fetch and check ahead/behind against `origin` before pushing.

---

# Coding Standards

Follow the existing project standards.

Maintain:

- Folder structure
- Naming conventions
- Architecture patterns
- Error handling patterns
- API conventions
- Component patterns
- State management patterns

Prefer modifying existing code over creating duplicate solutions.

Write clean, readable, maintainable code.

Avoid:

- Dead code
- Duplicate logic
- Unnecessary abstractions
- Over-engineering

---

# Architecture Protection

Respect the existing architecture.

Do not:

- Introduce new patterns without justification
- Rewrite working systems unnecessarily
- Change public APIs unexpectedly
- Replace libraries without a reason
- Create unnecessary dependencies

Maintain backward compatibility whenever possible.

---

# Security Review

Every code change must include a security review.

Review:

## Authentication

- Login flows
- Sessions
- Tokens
- Password handling
- Identity verification

## Authorization

- Permissions
- Roles
- Access controls
- Resource ownership checks

## Data Protection

- Sensitive data exposure
- Logging
- Encryption
- Secrets management

## Input and Output Safety

Check:

- Input validation
- Output handling
- User-generated content
- File uploads
- API inputs

## Application Security

Review for:

- Injection risks
- Authentication bypass
- Authorization bypass
- Unsafe defaults
- Excessive permissions
- Information leakage

---

# Data Integrity Standards

Protect user data above all else.

Never:

- Delete user data without explicit approval
- Perform destructive migrations
- Remove production records
- Change schemas without considering existing data

Always review:

- Database migrations
- Transactions
- Rollbacks
- Validation
- Foreign keys
- Relationships
- Cascade behavior
- Duplicate records
- Race conditions
- Data consistency

Prefer additive changes.

Ensure migrations can be safely reversed when possible.

**Concrete rule for this codebase (`moleculeid-api`):** never `ALTER` the `compounds` table. If a new feature needs to persist or cache data, create a **new side-table** via `CREATE TABLE IF NOT EXISTS` + `ON CONFLICT DO UPDATE` (the established pattern — see Repository Map). This has zero migration risk versus altering a live production table with real user/library data in it.

---

# Regression Review

Every change must consider existing functionality.

Review:

- Existing features
- User workflows
- Authentication flows
- Authorization rules
- APIs
- Database operations
- UI behavior
- Navigation
- Routing
- Mobile behavior
- Responsive layouts
- Accessibility
- Error states
- Loading states
- Empty states

Assume changes can create regressions until verified.

When extending a **working, live feature**, prove non-regression concretely: diff the changed file and confirm no existing line was modified (only additions), and test that if the new code path fails or is unavailable, the feature falls back to its exact prior behavior.

---

# Performance Review

Review changes for:

- Slow queries
- N+1 queries
- Excessive API calls
- Large bundle increases
- Memory leaks
- Inefficient rendering
- Expensive calculations
- Missing indexes
- Poor caching decisions

Do not introduce unnecessary performance degradation.

---

# Testing Requirements

Every completed feature or change must be validated.

Run applicable:

- Build checks
- Lint checks
- Type checks
- Unit tests
- Integration tests
- End-to-end tests

If tests do not exist:

- Add tests where appropriate.
- Explain manual verification steps.

If tests cannot be run:

Clearly state:

- What was not tested
- Why it was not tested
- What alternative validation was performed

Never claim tests were run when they were not.

**Known constraint across these repos:** most routes require a live Supabase login, which is not available in this working environment. When a route can't be exercised live, test the underlying function directly instead — import the real module and mock only the true I/O boundary (the DB query call, the external HTTP call), not a hand-copied reimplementation of the logic, since a hand-copy can silently drift from the real code. State plainly that live UI verification is still outstanding and needs a human smoke test.

---

# Error Handling Requirements

Verify:

- Invalid inputs
- Missing values
- Failed requests
- Timeouts
- Unexpected states
- Recovery behavior
- User-facing error messages

Failures should be handled gracefully.

---

# Documentation Requirements

Update documentation when changes require it.

Document:

- New features
- Configuration changes
- Environment variables
- API changes
- Database migrations
- Deployment requirements
- Breaking changes

---

# Deployment Checklist

Before recommending deployment verify:

- Build succeeds
- Tests pass
- No lint errors
- No type errors
- Security review completed
- Data integrity reviewed
- Regression review completed
- Documentation updated
- Migration steps documented
- Rollback considerations documented

Do not recommend deployment if critical issues remain unresolved.

**Deploy mechanics in this environment:** pushing to `main` is the deploy trigger (Vercel for `moleculeid-web`/`veromass-web`, Render for `moleculeid-api` — see Repository Map). Claude can verify a commit was pushed to the correct branch, but cannot see Vercel/Render build logs or confirm a deploy actually succeeded — say so explicitly rather than implying "deployed" means "confirmed live."

---

# Self Review

Do not assume your first implementation is correct.

Before completing work, review your own changes as if you were a senior engineer reviewing a production pull request.

Look for:

- Bugs
- Logic errors
- Security concerns
- Missing validation
- Edge cases
- Performance issues
- Maintainability problems
- Missing tests

Fix discovered issues before presenting the final result whenever possible.

---

# AI Behavior Rules

Do not guess.

Do not invent:

- APIs
- Database tables
- Database columns
- Environment variables
- Libraries
- Configuration values

If information is missing, ask.

Clearly state assumptions.

Separate:

- What was verified
- What was reviewed manually
- What could not be verified

**Verify the unit of analysis, not just that the code runs.** Before building any feature that groups/compares/aggregates data, confirm what the grouping key actually represents in the real schema — don't infer it from what similar-looking existing code does. (This bit us directly: `chrom_id` was assumed to be a user's experimental batch because other features grouped by it, but it's actually a library-*construction* run ID. The math was correct; the unit was wrong, and it wasn't caught until user testing.)

---

# Completion Requirements

A task is complete only when:

- The feature is implemented.
- Existing functionality has been considered.
- Code has been reviewed.
- Security considerations have been reviewed.
- Data integrity has been considered.
- Testing has been performed or limitations documented.
- Risks have been identified.
- Deployment considerations have been documented.

Writing code alone does not mean the task is complete.

**Status must reflect reality, not effort.** In ClickUp: `in development` while building, `testing` once deployed but not yet confirmed by a human, `shipped` only after the user explicitly confirms it works. Deployed code that hasn't been verified live is not "done." When a task moves to `testing`, post concrete tester-facing steps and expected outcomes as a comment.

---

# Final Response Format

**This scales with the Risk Classification above.** For Low-risk changes (copy, styling, docs, minor UI), give a brief summary of what changed and skip the rest — a full 8-section report on a color tweak is noise, not rigor. For Medium/High-risk changes, include the sections below.

## Summary

What changed.

## Files Modified

List changed files.

## Implementation Details

Explain the approach taken.

## Testing

Include:

- Tests run
- Results
- Manual verification
- Tests not performed and why

## Security Review

Include:

- Authentication impact
- Authorization impact
- Data handling impact
- Risks identified

## Regression Review

Include:

- Existing functionality checked
- Compatibility considerations

## Risks and Follow-Up

Include:

- Remaining risks
- Recommended future improvements

## Deployment Notes

Include:

- Configuration changes
- Migration requirements
- Rollback considerations

Always be transparent about limitations.

---

# Repository Map

Verified facts only — repos not listed here (or marked "undocumented") have not been reviewed in depth; do not assume patterns from one repo apply to another without checking.

## moleculeid-api (FastAPI backend, deploys to Render via `render.yaml`, push to `main` triggers deploy)
- Single `compounds` table serves as BOTH the reference library (name/formula/SMILES/compound_class/adduct m/z-rt columns) AND per-library-batch match results (`chrom_id`, `pos_matched`/`neg_matched`, `pos_intensity`/`neg_intensity`). **`chrom_id` identifies a library-construction run, not a user's experimental sample** — see the AI Behavior Rules note above.
- New feature pattern: a standalone module (e.g. `group_stats.py`, `id_conversion.py`, `batch_correction.py`) with `router = APIRouter()`, a module-level `_require_auth`/`set_auth_dependency(fn)` pair, and an `_auth_guard`/`_auth` dependency wrapping the real JWT verifier. Registered in `main.py` with exactly 4 additive lines: import router, import module, `X_mod.set_auth_dependency(require_auth)`, `app.include_router(X_router)`. Never edit existing route logic to add a new one.
- Persistent caching: new side-table via `CREATE TABLE IF NOT EXISTS` + `ON CONFLICT DO UPDATE` (established by `compound_targets`, `compound_pathways`, `compound_access`, `compound_ids`). Never `ALTER` `compounds`.
- External API calls (KEGG, PubChem, ChEMBL, Reactome): wrap in a helper that never raises, url-quote all user input with `safe=''`, rate-limit/timeout per call, cap batch size per request.
- Auth: Supabase ES256 JWT verified via `require_auth` in `main.py`; tier read live from `auth.users` (not trusted from a possibly-stale JWT claim) via `_get_tier`.

## moleculeid-web (React/Vite, deploys to `app.veromass.com` via Vercel, push to `main` triggers deploy)
- `Analysis.jsx` uses a tab pattern (`TABS` array + `TAB_INTRO` descriptions + conditional render) — new analysis features become new tabs here.
- `Library.jsx` is large/complex; prefer new features as self-contained components in their own file (e.g. `IdConverter.jsx`) wired in with minimal footprint (one import, one state var, one button, one conditional render) rather than editing its internals directly.
- Design tokens in `design.js` (`export const T = {...}`) — reuse existing color/font/spacing tokens rather than hardcoding new ones.
- No charting library in this codebase — visualizations are hand-rolled SVG (see `PCAScatter` in `Analysis.jsx`, mirror plots in `Masst.jsx`).
- Most routes require a live Supabase session — cannot be exercised end-to-end without real login credentials.

## veromass-web (static marketing site, single `index.html`, push to `main` triggers deploy — host unconfirmed)
- No build step. Design system: Outfit (sans)/Lora (serif accent)/JetBrains Mono, teal `#00A882`/`#00c49a` + purple `#5266eb` accents.
- Verification approach: screenshot tooling in this environment is unreliable — use `javascript_tool`/DOM queries or `get_page_text` instead of screenshots to verify changes.

## veromass-utils (utility scripts, e.g. `tools/import_compounds.py` for Excel → Supabase `compounds` imports)
- Not deeply reviewed. Known: real uncommitted work has sat in this repo before without anyone noticing (SMILES/class/type column mapping) — check `git status` here specifically before assuming it's clean.

## excalibar (VOLTA desktop app, Python/Streamlit, distributed as `VOLTA.exe` via PyInstaller)
- Not deeply reviewed this cycle.

## Undocumented (present under `repos/` but not reviewed in this work)
`mgf-extractor`, `phyto-crossmatcher`, `MoleculeID_Processor`, `moleculeid-compound-prediction-models`, `Supabase Import Tools`, `lcms-platform`. Do not assume any pattern above applies to these — review each on its own terms before working in it.
