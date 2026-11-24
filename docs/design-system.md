# Design system: how to build one and work with it in Claude

A how-to guide for React/TypeScript frontends.
The rules the model uses on every view are in the skill
[`building-ui`](../skills/building-ui/SKILL.md).

## Why

The model knows design principles, but every session designs from scratch. Without a design system you get
different spacing, shades and buttons on every screen, and everything looks "AI-made".
A design system turns taste into **constraints in code**. A model that has
`<Button variant="secondary">` and `--space-4` at hand won't invent a 14th shade of gray.

## What it consists of

| Layer | What it is | Where in the project repo |
|---|---|---|
| **Tokens** | colors, spacing, typography, radii, shadows, motion, density, in 3 layers: primitives → semantic → themes | `src/styles/tokens.css` (or `@theme` in Tailwind v4) |
| **Base components** | Button, Input, Select, Dialog, Table, Tabs, Toast… | `src/components/ui/` (or `packages/ui/` in a monorepo) |
| **Patterns** | composite layouts: "map + panel", "table with filters", "content page", "dashboard" | `src/components/patterns/` |
| **Living documentation** | Storybook: every component and state as a story, generated from code, so it doesn't go stale | `*.stories.tsx` |
| **Enforcement** | lint that forbids raw values, visual tests of stories | ESLint/stylelint config, Playwright |

## Phase 0: decisions (one session with Claude, output: ADR)

Best done in `/grill-with-docs`: the interview adds terms to `CONTEXT.md` and writes the ADR right away.

1. Tell Claude about the product: who uses it (foresters, enthusiasts, students), on what (a phone
   in the field, a desktop in the office), what character (calm, content-focused, no marketing), what density
   (blog and edu comfortable; maps, statistics and the validator compact).
2. Pick a foundation. Typical options:
   - **shadcn/ui + Tailwind v4**: components copied into the repo (full control), Radix underneath
     (accessibility), tokens as CSS variables. A good default choice.
   - **Mantine**: a ready, rich library (tables, dates, forms), less code to maintain,
     less freedom over the look.
   - **Radix Primitives + your own styles**: maximum control, most work.
3. An ADR "Design system foundation" with the choice and the rejected options. `/grill-with-docs` writes it
   itself; outside grilling, ask for it directly (skill `domain-modeling`).
4. Unsure how the key screens should look? `/prototype` (UI variants) before Phase 1.

## Phase 1: tokens

```
You: "Propose tokens for the forest platform based on assets/tokens.css from building-ui"
Claude: copies the starter file, adjusts the palette (accent, neutrals), the type scale and density,
        checks contrast in both themes
You: look at the "Tokens" page in Storybook (palette, scale, typography) and make corrections
```

Rules:
- Components use **only semantic tokens** (`--color-text-muted`), never primitives
  (`--neutral-600`). Changing a theme is then an edit to one layer.
- One accent (here forest green). `danger`/`warning`/`info`/`success` colors only when they carry meaning.
- Contrast per WCAG 2.2: text ≥ 4.5:1, control outlines ≥ 3:1. The starter file is already checked,
  but you recheck every color change.
- Palettes for maps and charts (sequential, diverging, categorical, colorblind-safe)
  are tokens too. See `references/data-dense-and-maps.md` in `building-ui`.

## Phase 2: base components

1. List the platform's screens (blog, post, profile, chat, edu, map, statistics, validator) and ask
   Claude for a **component inventory**: what all the screens need.
2. You build from primitives to composites: Button, Input, Label → FormField → Dialog → Table → patterns.
3. Every component gets a story with **all states**: default, hover/focus, disabled, loading,
   error, long text, both themes, both densities.
4. After each component: `/damstack:review-changes`. `frontend-reviewer` checks accessibility
   and consistency, and if Storybook is running, takes screenshots.

This stage is a good candidate for `/damstack:mentor`. Tokens and accessible components (focus trap in Dialog,
ARIA roles in Tabs) are worth writing yourself at least once.

## Phase 3: enforcement

What can be checked automatically doesn't go into the prompt:
- ESLint: ban arbitrary values in Tailwind classes (a rule from the Tailwind ESLint plugin,
  e.g. `no-arbitrary-value`, depending on the plugin version). stylelint: `declaration-strict-value`
  for colors in CSS.
- Visual tests: Playwright `toHaveScreenshot()` on stories. They are stable, unlike
  map tiles.
- CI: lint + visual component tests on changes in `components/ui/`.
- The project's `CLAUDE.md`: the **Design** section from the template (`skills/setup-damstack/assets/CLAUDE.project.md`), that is
  where the tokens and components are, the product's character, density, rules for UI copy.

## Daily work with Claude

### New screen

```
1. "Build an observations list view with a species filter and a map"
2. Claude (skill building-ui): first 3–5 lines on the screen's goal, primary action and regions
     → you accept or correct the structure before any code is written
3. Implementation only from DS components and tokens, with all states
4. Visual loop: screenshots at 375 px and 1280 px (+ dark), Claude looks and fixes
5. /damstack:review-changes → frontend-reviewer (code + screenshots) → fixes
```

### A component is missing

You don't make a one-off component inside a feature. Order: component in `components/ui/`
+ story + review, and only then use it in the feature. Claude should propose this on its own.
If it doesn't, `frontend-reviewer` will flag the duplicate.

### Changing a token

1. Change in the semantic layer (e.g. `--color-accent`).
2. Screenshots of key stories and screens before and after. With visual tests, Playwright shows the differences.
3. Contrast check.
4. A significant change (new accent, new scale)? A new ADR that supersedes the previous one.

### You have mockups in Figma

If you design in Figma, connect the Figma connector. Claude will read the mockup, but implements
**from DS components and tokens**, not from values hardcoded from the mockup. A mismatch
between the mockup and the tokens is a question for you, not a reason to add a new color.

## Anti-patterns

- A style written directly in a feature "because it's only here": after a month you have 5 versions of the same button.
- Blindly copying a dashboard template from the internet: that is marketing aesthetics in a work tool.
- Tokens as the only documentation ("it's in the CSS"): without Storybook nobody, including the model,
  can see what already exists.
- "Looks OK" without a screenshot: the model doesn't see the UI until it renders it and looks at it.
- Color as the only carrier of information (statuses, map legend).
