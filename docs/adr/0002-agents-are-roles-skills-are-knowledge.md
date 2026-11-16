# ADR-0002: Agents are roles, technology knowledge lives in skills

- Status: Accepted
- Date: 2026-09-29

## Context

It is tempting to create expert agents (`python-expert`, `django-expert`, `k8s-expert`). A subagent,
however, starts without the conversation context, and handing over a task loses what was agreed.
"Expertise" alone adds little, because the model already knows these technologies. The first version
of the agents also had long stack-specific checklists written into the reviewer prompts. This
scatters attention and pushes the model to report something in every category.

## Decision

- A subagent is created only when it provides: context isolation (lots of reading, logs, web pages),
  different permissions (read-only), parallelism or an independent view (review).
- Agents are stack-agnostic: role, method, output format.
- Technology knowledge lives in skills. They load on demand (by description or `paths`) or are
  preloaded into an agent via `skills:`.
- Facts about a specific project live in that project's `CLAUDE.md`.

## Alternatives considered

- **Expert agents per technology**: they lose the conversation context, and knowledge is duplicated across agents.
- **Everything in one large `CLAUDE.md`**: it always loads and eats context even when it is not needed.

## Consequences

- Knowledge about e.g. PostGIS is written once and used by the main session, `postgres-reviewer`
  and `implementation-worker`.
- A new technology means a new skill, not a new agent.
- Reviewers share the `review-standards` skill (weights, evidence, finding format).
