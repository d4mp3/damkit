---
name: adr
description: Use when an architectural or technology decision is being made or was just made - choosing a library, database design, storage CRS, service boundaries, deployment or CI approach, security model, data format, or reversing an earlier decision - and when the user asks to record, write or supersede an ADR (Architecture Decision Record).
argument-hint: "[decision title]"
---

# Architecture Decision Records

An ADR records **one decision, its context and the alternatives rejected**, at the moment it was
made. It doesn't go stale because it never claims to describe the present, only what was
decided and why. It answers the question the code can't: "why is it like this?"

## When a decision deserves an ADR

Write one when at least one of these holds:
- it is expensive to reverse (data model, CRS, framework, service split, a GitOps layout)
- real alternatives were considered and rejected
- future-you or an AI assistant would plausibly "fix" it back to the rejected option
- it constrains other code (e.g. "all geometries are stored in EPSG:2180")

Don't write one for choices that are reversible in minutes or dictated by existing conventions.

If you are in a conversation where such a decision just happened, **offer** to record it
(one sentence). Write the file when the user agrees, or when they invoked this skill.

## Procedure

1. Find the ADR directory: `docs/adr/` (or an existing `doc/adr`, `docs/decisions`). Create
   `docs/adr/` if none exists.
2. Next number = highest existing + 1, zero-padded to 4 digits. Filename:
   `NNNN-kebab-case-title.md`.
3. Fill in `${CLAUDE_PLUGIN_ROOT}/skills/adr/template.md`. Take the context, the alternatives and the reasons **from the
   conversation**: they are the valuable part. Don't invent alternatives that weren't
   considered. If the reasons for rejecting an option are unknown, ask the user.
4. Keep it to about one page. Link to the code, issues or benchmarks instead of pasting them.
5. Status: `Proposed` while undecided, `Accepted` once agreed.

## Changing a decision

- Never rewrite an accepted ADR's content. Create a new ADR that says
  `Supersedes: ADR-NNNN`, and change only the old ADR's status line to
  `Superseded by ADR-MMMM`.
- Typos and broken links may be fixed in place.

## After writing

- If the decision constrains everyday coding, add a one-line pointer to the project's CLAUDE.md
  (`- Geometries stored in EPSG:2180, see docs/adr/0003-storage-crs.md`).
- Reference the ADR from the code where it matters (a comment containing `ADR-NNNN`).
