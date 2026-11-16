# ADR-0015: QRSPI steps extend Matt's flow: `to-research-questions` and `to-design-discussion`

- Status: Accepted
- Date: 2026-10-07
- Amends: ADR-0013 (devkit may add a process step where Matt's flow has none)

## Context

ADR-0013 handed the whole process to Matt's skills, so that devkit wouldn't compete with them for triggers. Matt's
flow, however, has two gaps that show up with tickets in existing code the session doesn't know:

- **Research is biased.** `/research` or grilling with the ticket in context makes
  the model look for code that fits the solution it has already imagined, and skip what gets in its way.
  Facts about the current code and the intent of the change get mixed before anyone has decided what to do.
- **There is no point for a design review before the spec.** Right after `/grill-with-docs`, the spec
  and tickets are created. The code owner, who knows which pattern the team abandoned or what is in progress, sees
  the change only in the code, when a fix costs a rewrite instead of a sentence.

None of Matt's skills does either of these things, so adding them doesn't duplicate his steps.

## Decision

- Devkit may add a process step only where Matt's flow has none. The step hands its output to
  one of Matt's steps, reads his `docs/agents/*.md` and uses terms from `CONTEXT.md`.
  It neither replaces nor edits Matt's steps.
- `to-research-questions`: ticket → 6–8 questions about the current state of the code, without the intent (leak test).
  `/research` answers them in a fresh session, and the file with the answers goes together with the ticket
  into `/grill-with-docs`. The researcher's blindness works only through a real context boundary.
- `to-design-discussion`: after `/grill-with-docs` → a document of about 200 lines for the code owner
  (current state, target state, Follow/Avoid patterns, decisions D1…, open questions). Every
  pointer to code is verified. Review comments are resolved in the same session, then `/to-spec`.
- Both steps are optional. A small change or code the session knows goes straight through `/grill-with-docs`.
- A QRSPI step's description names the artifact it produces ("Turn a ticket into research questions…").
  The artifact's name is the word I invoke it with, so the "description = when to use it" rule
  for knowledge skills doesn't cover them.
- The connection to the flow lives in `## Workflow` of the project `CLAUDE.md` template, like the Risk axis.

## Alternatives considered

- **Stay with Matt's flow alone**: research with the ticket in context and no design review
  before the spec. These problems surface only in the code.
- **Add these steps to Matt's skills**: Matt's skills are updated
  from upstream (ADR-0013), and editing them would mean manual merging on every update.
- **Research through a subagent from the same session instead of a fresh session**: I write the subagent's prompt
  with the ticket in my head, so the intent leaks easily. The subagent remains as a fallback
  option with a manual check of the prompt.

## Consequences

- The full flow for unfamiliar code: `/to-research-questions` → `/research` (fresh session) →
  `/grill-with-docs` → `/to-design-discussion` → code owner review → `/to-spec` → `/to-tickets` → `/implement`.
- Without Matt's skills, neither step works: they read `docs/agents/*.md` and hand their output to his steps.
- A new process step in devkit requires showing a gap in Matt's flow and the step it hands its output to.
- The `codex/` variant doesn't have them yet (ADR-0011).
