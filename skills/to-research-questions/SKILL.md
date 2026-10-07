---
name: "to-research-questions"
description: "Turn a ticket (URL, path or description) into research questions about the current code, so a blind researcher can answer them without learning what is being built."
---

# To Research Questions

Turn a ticket into **research questions**: a short list of questions about the **current state** of the codebase that someone must answer before the work can be designed. The questions go to a **blind researcher**, an agent in a fresh context that never sees the ticket. It describes what exists; it has no goal to argue for, so it cannot slip opinions into the facts.

The split is the point. A researcher that knows the goal starts designing: it reports the code that supports its preferred solution and skips the code that complicates it. This skill is the only step that holds both the ticket and the codebase; everything it hands on carries the **area**, never the **intent**.

The issue tracker and domain doc layout should have been provided to you (`docs/agents/issue-tracker.md`, `docs/agents/domain.md`). If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Fetch the ticket

The argument is one of three things:

- **A URL or issue number** → fetch it as `docs/agents/issue-tracker.md` describes (`gh issue view <n> --comments`, `glab issue view`, …), body and comments.
- **A path** → read the file.
- **Prose** → that is the ticket.

Done when you hold the ticket's full text, comments included.

### 2. Orient, without investigating

Read `CONTEXT.md` and the ADRs touching this area, as `docs/agents/domain.md` describes. Skim the directory layout and open files only far enough to know **where** each concept in the ticket lives: which modules, tables, jobs, endpoints.

Stop at _where_. A file's exports, a table's columns and a registry's entries tell you where; following a function body or a call chain tells you how. Knowing how is research done with the intent in your context, which is exactly what this skill exists to avoid; leave it to the researcher, even when a small file hands you the answer.

Done when you can name every area of the codebase the ticket touches, in the glossary's vocabulary.

### 3. Draft the questions

Aim for **6–8 questions**. A small ticket may need 4; a wide one up to 10. Needing more than 10 means the ticket spans several pieces of work: say so and suggest splitting it before research.

Each question:

- Asks how something **works now**: what exists, where it lives, how data flows, what calls what, what happens when. Answerable from code, config, schema, tests or git history.
- Targets **one mechanism**: one table, one flow, one job. Up to three facets of that mechanism may follow a colon ("…: its columns, types and nullability"); a fourth facet, or a second mechanism, is a second question.
- Leaves the answer out. When orientation showed you something, ask about it; writing what you saw into the question hands the researcher your reading instead of its own.
- Names existing things in the glossary's vocabulary, so the researcher searches for the right words.

Cover the vertical slice the work will cut through. Use this list as a coverage check, not a template; skip what the ticket never touches:

- **Entry points**: the routes, commands, jobs or UI that start the relevant flows.
- **Data**: where the relevant state is stored, its shape and types, units and time zones, nullability.
- **Flow**: how a request or event travels through the layers involved.
- **Side effects and integrations**: email, queues, third-party APIs, caches, events emitted.
- **Prior art**: existing features that already solve a similar problem, and how. This is often the most valuable question: it surfaces the pattern to copy, and the deprecated one to avoid.
- **Rules and constraints**: permissions, tenancy, rate limits, feature flags, performance-sensitive paths.
- **Testing**: how this area is tested today (fakes, fixtures, integration harness).

Order them foundational-first: a later question may lean on an earlier answer.

Done when the list covers every area from step 2.

### 4. Run the leak test

Reread the list as the blind researcher. The area may show: asking about the email path tells it you care about email, and that is fine. Taken together the areas may even narrow its guess; that is fine too, since a guess is not a goal it can argue for. The **intent** must not show: it should be unable to say what is being built or why.

Rewrite every question that names the new feature, speaks in the future or conditional ("should", "will", "would", "how could we"), or ties a fact to a purpose ("…so that we can add X"). Restate it as a question about what exists.

| Leaks intent | Neutral |
| --- | --- |
| How should we send the overdue reminder email? | How does the application send email today, and from which callers? |
| Where would a daily digest job fit in the scheduler? | How are recurring background jobs registered and scheduled? |
| Can `notification_preferences` support opting out of reminders? | What is the shape of `notification_preferences`, and where is it read? |

Done when no question names the new feature or uses a verb of change.

### 5. Write the file

Save it where the repo already keeps research notes, matching the existing convention; with none, use `docs/research/`. Name it after the **area**, not the feature (`notifications-and-jobs-questions.md`, not `overdue-reminders-questions.md`): the filename is the first thing the researcher reads.

Write the file in the language of the repo's docs. Use this template, and put nothing else in it: no ticket link, no title or goal of the work.

<questions-template>

# Research questions: <area>

**Scope:** <the areas of the codebase these questions cover, one line>

## How to answer

- Describe how the code works today. Make no recommendations and propose no changes.
- Cite every claim with a path and symbol or line (`src/notifications/queue.ts:enqueueNotification`).
- When something can't be found, write "Not found" and where you looked, rather than inferring.
- Note contradictions you come across: two implementations of one thing, a comment that disagrees with the code, a deprecated path still in use.

## Questions

1. <question>
2. <question>

</questions-template>

Done when the file exists, passes the leak test, and you have reported its path.

### 6. Hand off to the blind researcher

The researcher's blindness only holds across a real context boundary. An agent dispatched from this session inherits whatever its prompt carries, and you are the one writing that prompt with the ticket in mind. Give the user two ways forward:

- **Fresh session (recommended).** Open a new session and run `/research Answer the questions in <path>. Follow the "How to answer" section.` Pass nothing else: no ticket, no summary of this conversation.
- **Subagent from here.** Only if the user wants it now and you can spawn one: dispatch it with a prompt containing just that same line. Read the prompt back before sending: if any word of it would let the researcher guess the intent, cut it.

The answers belong beside the questions as `<area>-research.md`. They feed `/grill-with-docs` next, together with the ticket: that is where facts meet intent, and where the human decides what to do with them.