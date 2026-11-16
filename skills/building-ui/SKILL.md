---
name: building-ui
description: Use when creating or changing user-facing UI in a web frontend - new pages, views, layouts, components, dashboards, forms, tables, map screens, styling or theming - or when a UI looks generic, inconsistent, cluttered, unpolished or breaks on mobile, or when setting up or extending a design system (tokens, component library, Storybook).
paths:
  - "**/*.css"
  - "**/tailwind.config.*"
  - "**/components/ui/**"
  - "**/packages/ui/**"
  - "**/*.stories.tsx"
---

# Building UI

Good UI in a codebase comes from **constraints plus looking at the result**, not from taste
described in prose. Use the design system, design every state, and verify visually before
calling it done.

## 1. Find the design system first

Look for: a tokens file (`tokens.css`, `@theme` in the Tailwind v4 CSS, `tailwind.config.*`),
`components/ui/` or `packages/ui/`, Storybook stories, and the project's CLAUDE.md "Design" section.

- **It exists:** use only its tokens and components. If a component is missing, propose adding it
  **to the design system** (with a story), not a one-off in the feature.
- **It doesn't exist:** don't invent styles inline. Propose a minimal foundation based on
  `${CLAUDE_PLUGIN_ROOT}/skills/building-ui/assets/tokens.css` and a component library, and ask before establishing it.
  That is a decision worth an ADR (via the domain-modeling skill).

## 2. Decide what the screen is for (before code, for new screens)

If the layout itself is still an open question (several plausible structures, nobody can pick
on paper), answer it first with `/prototype` (UI variants on a throwaway route). This skill
builds the chosen structure for real, inside the design system.

Write 3–5 lines: the user's main task, the **one** primary action, the data density
(a marketing page, a content page or a data-heavy tool), and the regions (e.g. "filters | map | detail panel").
Data-heavy and map screens have their own patterns: `references/data-dense-and-maps.md`.

## 3. Build rules

- **Tokens only.** No raw hex or rgb, no pixel values outside the scale, and no arbitrary Tailwind values
  (`p-[13px]`, `text-[#333]`). A value the scale lacks is a design-system question.
- **Hierarchy through size, weight and space first, and color last.** Use one accent color. Semantic colors
  (danger, warning, success) only carry meaning.
- **Real content.** Write copy in the project's UI language (`## Language` in `CLAUDE.md`; ask once
  if it's missing) with realistic lengths (long proper names such as "Nadleśnictwo Krościenko", long
  species names), numbers and dates through `Intl` with the project's locale, and units. No lorem ipsum.
- **One primary button per view.** Destructive actions are visually distinct and confirmed.
- **Accessibility is visual too.** Contrast ≥ 4.5:1 for text and ≥ 3:1 for UI parts. Focus stays visible.
  Never rely on color alone (legends, statuses). Targets ≥ 24×24 px, and 44 px on touch. Respect
  `prefers-reduced-motion`.

## 4. Every view has all its states

| State | What it shows |
|---|---|
| loading | a skeleton in the final layout's shape (no layout jump), not a lone spinner for a whole page |
| empty | why it's empty, plus the next action ("Add your first observation", in the UI language) |
| error | what failed in human terms, plus retry. Keep the rest of the page usable. |
| overflow | long text (truncate with a tooltip or wrap), and 0 / 1 / 1000 items (pagination or virtualization) |
| permission | hidden vs disabled-with-explanation, chosen consistently |

## 5. Avoid the generic "AI look"

Default gradients, cards inside cards, centering everything, emoji as icons, shadow + border +
large radius stacked on everything, more than 2–3 font weights, decorative illustrations in a tool
UI, and every section styled differently. Prefer restraint: a neutral scale, one accent,
consistent spacing rhythm, and alignment to a grid.

## 6. Verify visually (required before saying "done")

Use a running dev server or Storybook (reuse one if it is already up: `curl -sI localhost:5173`).

```bash
npx playwright screenshot --viewport-size "375,812"  --full-page http://localhost:5173/path /tmp/ui-mobile.png
npx playwright screenshot --viewport-size "1280,800" --full-page http://localhost:5173/path /tmp/ui-desktop.png
npx playwright screenshot --viewport-size "1280,800" --color-scheme dark http://localhost:5173/path /tmp/ui-dark.png  # if dark mode exists
```

Open the PNGs (the Read tool shows images) and check alignment, spacing rhythm, hierarchy (is the primary
action obvious in 3 seconds?), overflow, and contrast. Force other states through Storybook stories,
MSW handlers or query params, and screenshot them too. Fix what you see and re-shoot. If the browser
tools are available (claude-in-chrome), you can use them instead.

If you can't run the UI, say plainly that visual verification was not done. Don't claim it looks right.

## 7. Report

State which design-system components and tokens were used, any tokens or components you propose adding,
which states and viewports you verified, and the screenshot paths.
