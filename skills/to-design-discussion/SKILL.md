---
name: "to-design-discussion"
description: "Turn a grilled conversation into a ~200-line design discussion for a code owner to review before coding: current state, end state, patterns, decisions, open questions."
---

# To Design Discussion

Turn what the current conversation has settled into a **design discussion**: a short document that makes the **design concept**, the shared understanding between the user and the agent of what is being built and how it fits the codebase, reviewable by someone who was not in the room.

Its reader is a **code owner**: they know the codebase better than anyone in this conversation and have ten minutes. They will catch what the conversation could not: the pattern the agent is about to copy that the team abandoned last year, the decision that clashes with work in flight. Correcting the design here costs a sentence; correcting it after implementation costs a rewrite. That is the leverage: around 200 lines reviewed now, instead of a plan as long as the code, or the code itself, reviewed later.

Do NOT interview the user. Synthesize what the conversation and its artifacts already contain. Anything unsettled becomes an open question in the document, not a question in chat.

The domain doc layout should have been provided to you (`docs/agents/domain.md`). If not, tell the user to run `/setup-matt-pocock-skills`.

## Process

### 1. Gather the sources

Collect what the design rests on:

- The conversation itself, usually a `/grill-with-docs` session: the primary source.
- The ticket, and any research file (`*-research.md`) the conversation used. If the user passed paths or a ticket reference as arguments, read them in full.
- `CONTEXT.md` and the ADRs written or touched during the conversation.

Done when you can list every decision the conversation reached and every question it left open.

### 2. Check every pointer against the code

Each claim about the current state and each pattern you recommend gets a **pointer**: a path plus a symbol or line. Open each one and confirm it still says what you are about to claim.

The reviewer will spot-check pointers, and one wrong pointer costs the whole document its credibility. When the code disagrees with the research file or the conversation, the code wins: write what the code says, and add the disagreement to Open questions. A decision the conversation reached on a premise the code contradicts stays under Decisions as agreed, with a reference to the open question that challenges it; the reviewer needs to see both.

A pointer you cannot open (a module outside the repo, a missing helper) supports no claim. State the gap instead, and add it to Open questions when the design depends on it.

Done when every pointer you intend to use has been opened in this step.

### 3. Write the document

Use the template below. Write in the glossary's vocabulary, and in the language of the repo's docs.

The budget is **about 200 lines**; 150 to 250 is fine. When over, cut Current state narrative first. Decisions and Patterns are where the review value lives, so they are the last to shrink. A file-by-file plan, code beyond a signature, and the test plan belong to `/to-spec`, which comes next.

When a decision contradicts an existing ADR, say so in that decision, as `docs/agents/domain.md` describes.

<design-discussion-template>

# Design discussion: <feature name>

**Ticket:** <link or path> · **Research:** <path, if any> · **Reviewer:** <code owner, if known>

## Summary

Two or three sentences: what changes, for whom, and the single decision the reviewer most needs to check.

## Current state

How the relevant parts of the system work today, limited to what the change touches. One short paragraph or a few bullets per area, each claim with its pointer.

## Desired end state

What is observably different when the work is done, from the user's side and from the system's side. Describe the destination, not the route.

## Patterns

### Follow

Existing code the implementation should imitate. For each: the pointer, and one line on why it is the right exemplar for this change.

### Avoid

Code the implementation could plausibly copy but should not: deprecated paths, legacy duplicates, one-off workarounds. For each: the pointer, and why. This is the section most likely to save a rewrite; when the conversation surfaced none, look once more for older siblings of the patterns you listed under Follow.

## Decisions

Numbered, so the reviewer can answer "D3: disagree".

**D1. <decision in one line>**
Why: <the reason given in the conversation; when the user simply chose, say so rather than supplying a reason>. Rejected: <alternatives and why, when the conversation weighed any>. <ADR link, if one was recorded.>

## Open questions

Numbered. For each: what is undecided, what it blocks, and who can answer it if known. Mark assumptions the conversation made without anyone confirming them as **Assumption:**, so the reviewer can confirm or overturn them. Gaps you noticed while writing that the conversation never touched belong here too, marked **Not discussed:**, so the reviewer can tell them apart from what the user already weighed.

## Out of scope

What this change deliberately leaves alone, so the reviewer does not hunt for it.

</design-discussion-template>

Done when the document follows the template and every decision from step 1 appears under Decisions or Open questions.

### 4. Save it

Put it beside the feature's other artifacts. With a local-markdown tracker that is `.scratch/<feature-slug>/design-discussion.md`; otherwise wherever the repo keeps design notes, or `docs/design/<feature-slug>.md` when there is no convention. Offer to also post it on the ticket, as `docs/agents/issue-tracker.md` describes; post only if the user says yes.

Done when the file is saved and you have reported its path and line count.

### 5. Hand off for review

Tell the user who should read it (the reviewer they passed as an argument, else the code owner the conversation named) and what to ask them: check Patterns and Decisions first, answer the Open questions they can. Point out which open questions are the user's own to answer.

Stay in this session. Review comments come back into this conversation, which still holds the full reasoning behind each decision: resolve them here, update the document, then continue the main flow with `/to-spec` in the same context window.