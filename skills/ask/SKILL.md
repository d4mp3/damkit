---
name: ask
description: "Ask which damstack workflow, agent or skill fits your situation, and how it plugs into Matt Pocock's flow."
disable-model-invocation: true
argument-hint: "[your situation or question]"
---

# Ask damstack

The user describes a situation or asks how to get something done. Point them to the workflow that
fits, and walk them through it for *their* case. You guide; you don't run the workflow.

## 1. Read the map

Read `${CLAUDE_PLUGIN_ROOT}/docs/workflows.md`. It is the only source of damstack's workflows:
- "Find your situation" is the index to match the question against;
- "The main flow" is the path most work follows, and the three review axes;
- each workflow has a **When** line, numbered steps and **Watch out** points.

When the question is about one agent or skill (what it does, when to use it), also read the
`## Agents` or `## Skills` section of `${CLAUDE_PLUGIN_ROOT}/README.md`.

Answer from these files. Don't invent steps, commands or agents they don't contain.

## 2. Look at the project (read only, a few seconds)

Check what the answer depends on:
- `CLAUDE.md` with a `## Workflow` section: has `/damstack:setup-damstack` run?
- `skills-lock.json`, `.claude/skills/` or `docs/agents/`: are Matt's skills installed and set up?
- `## Language` in `CLAUDE.md`: the conversation language to answer in.

If setup is missing and the workflow needs it, make "Set up a new project" the first step of the answer.
If Matt's skills are absent, follow the "Without Matt's skills" section of the workflows file.

## 3. Match the question

- **One workflow fits:** use it.
- **Several fit in sequence** (e.g. a migration inside a larger feature): chain them in order and
  say where one hands over to the next.
- **The question is about Matt's process itself:** whether to continue, `/clear`, `/compact` or
  `/handoff`, `/wayfinder`, `/triage`, which grill to use. Send the user to `/ask-matt` in
  one line instead of answering from memory.
- **Nothing fits:** say so plainly. Then build the closest answer from the main flow and the
  agents and skills that apply, and label it as not a documented workflow.
- **The question is too vague to match** (e.g. "how do I start?"): ask one question that decides
  between the two or three likeliest workflows, naming them.

## 4. Answer in this shape

```
**Workflow:** <name>  (docs/workflows.md#<anchor>)
<one sentence: why it fits this situation>

**Steps for your case:**
1. <who acts> <what to type or do>, filled in with the user's details (file, ticket, table, app name)
2. ...

**Watch out:** <the 1–3 points from the workflow that apply here>

**Next:** <the workflow or step that follows, if any>
```

- Adapt the steps; don't paste the workflow. Put the user's names into the commands and prompts:
  `postgres-reviewer, assess this migration; the table has ~2M rows`, not `<N> rows`.
- Keep who acts explicit: **You**, **Claude**, or the agent's name.
- Refer to other workflows by name with `docs/workflows.md#<anchor>` in plain text, never as a bare
  `(#anchor)` link or a local absolute path: neither resolves in the user's terminal.
- Drop steps that don't apply, and say why in a few words when the reason isn't obvious.
- Keep it short: the user wants to act, not to read the whole file again.

## Rules

- Don't start the workflow, run commands or edit files. If the user then says "do it", that is a
  new request: they can run the first step themselves or ask you to.
- Use the terms of the workflows file and of the project's `CONTEXT.md`.
- When the docs and the project's `CLAUDE.md` `## Workflow` section disagree, the project wins:
  say so in the answer.
