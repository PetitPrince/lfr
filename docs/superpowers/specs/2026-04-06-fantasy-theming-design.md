# Fantasy Theming Design Spec

## Summary

Replace the placeholder Pico CSS styling on the player-facing side with a custom "Enchanted Parchment" theme. The dashboard (organizer/admin) stays on Pico CSS with only shared fonts and warm accent colors for brand consistency.

Readability is priority #1. The fantasy treatment is atmosphere, not distraction.

## Design Direction: Enchanted Parchment

Warm parchment backgrounds, gold/brown palette, moderate decorative elements. Cozy wizardry tone — a well-loved common room, not a dark dungeon.

## Typography

- **Headings:** Crimson Pro (serif) — weights 400, 600, italic 400
- **Body:** Source Sans 3 (sans-serif) — weights 400, 500, 600
- **Source:** Google Fonts, loaded via `<link>` with `preconnect`

## Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--parchment-light` | `#f5e6c8` | Page background (gradient start) |
| `--parchment-dark` | `#e8d5a8` | Page background (gradient end) |
| `--ink` | `#2c1810` | Primary text |
| `--ink-light` | `#5c3d2e` | Secondary text, section titles |
| `--gold` | `#d4a547` | Brand accent, nav brand text, active nav |
| `--gold-muted` | `#c4a265` | Borders, dividers, decorative elements |
| `--gold-dark` | `#6b5311` | Links, meta labels (darkened from #8b6914 for WCAG AA contrast) |
| `--brown-dark` | `#3d2b1f` | Nav background, primary buttons |
| `--brown-mid` | `#5c3d2e` | Nav background gradient end (intentionally same as --ink-light) |
| `--brown-muted` | `#8b6f4e` | Muted text, timestamps |
| `--card-bg` | `rgba(255,255,255,0.45)` | Card backgrounds |
| `--card-bg-hover` | `rgba(255,255,255,0.55)` | Card hover state |
| `--error` | `#8b3a3a` | Form validation errors, destructive actions |
| `--success` | `#3a6b3a` | Success flash messages |

House colors are stored in the database (House.color field already exists). Used for card top borders, house badges, and year badge borders.

## Layout

- **Max content width:** `70ch` for text-heavy pages (feed, post detail, forms)
- **Max page width:** `900px` for the overall page container
- **Centered single-column** layout for most pages
- **Two-column** layout only for student discover (220px filter sidebar + results)

## Navigation

Dark header bar with gradient (`#3d2b1f` to `#5c3d2e`), gold bottom border (3px solid `--gold-muted`).

- Brand text: run name flanked by decorative `*` characters, Crimson Pro, gold
- Links: Crimson Pro, `--gold-muted`, active link in `--gold`
- Items: Board, Discover (Faculty/Students/Other as sub-navigation or combined), Profile, Logout

## Components

### Cards

- Background: `--card-bg` with 1px `--gold-muted` border, 8px border-radius
- **Role tab:** Small label positioned at top-left of card, colored by role type (student uses house color, professor uses `--gold-dark`, staff uses `--brown-mid`)
- **House-colored top border:** 3px solid, color from house.color database field
- Padding: 16px (feed cards), 24px (detail card, forms)

### Badges

- **House badge:** Filled background (house color), light text, small rounded pill
- **Year badge:** Outlined (2px border in year color or house color), no fill
- **Keyword chips:** `rgba(196,146,101,0.3)` background, `--gold-muted` border, small rounded pill

### Buttons

- **Primary:** `--brown-dark` background, `--gold` text, Crimson Pro, 6px radius
- **Outline:** Transparent, `--ink-light` text, `--gold-muted` border
- **Destructive outline:** Same as outline but `#8b3a3a` color and border

### Form Inputs

- Background: `rgba(255,255,255,0.6)`
- Border: 1px solid `--gold-muted`
- Border-radius: 6px
- Font: Source Sans 3
- Color: `--ink`

### Dividers

Decorative flourish dividers between sections. Two styles:
- Dot-flourish-dot: `* ✸ *`
- Dash-flourish-dash: `—— ✻ ——`

Centered, `--gold-muted` color, letter-spacing 0.3em.

### Rumors (in feed and detail)

- Italic Crimson Pro text
- Left border: 2px/3px solid `--gold-muted`
- Padding-left for indent
- Opening/closing curly quotes in `--gold-muted`
- Background (detail view only): `rgba(196,162,101,0.1)`

### Comments

- Left border: 2px solid `--gold-muted`
- Nested replies indented 24px
- Author name: Crimson Pro semibold
- Timestamp: small, `--brown-muted`

### Flash Messages

- Container: card-style with left border accent (4px)
- Success: left border `--success`, `--success` text
- Error: left border `--error`, `--error` text
- Info: left border `--gold-dark`, `--ink-light` text

### Form Errors

- Field-level errors: `--error` text below the input
- Non-field errors: same as error flash message style

### Rumor Banner (Base Template)

The `{% random_rumor %}` tag renders an ambient rumor on every page. Styled as:
- Centered italic Crimson Pro text, `--ink-light` color, slightly reduced opacity (0.75)
- Curly quotes around the rumor text
- Character name link in `--gold-dark`
- Sits between nav and main content, no background — blends with the parchment
- Use `aria-hidden="true"` since it is decorative/ambient content

### Decorative Elements (Accessibility)

All decorative flourish dividers (`* [star] *`, `—— [star] ——`) must use `aria-hidden="true"` to avoid confusing screen readers. They are purely visual.

## Page Designs

### Standalone Pages (Landing, Login, Join)

These three pages are standalone HTML documents — they do **not** extend `base.html`. They must each independently link to `player.css` and Google Fonts. They share the same parchment background, fonts, and component styles as the rest of the player-facing pages, but have their own simplified nav (brand + optional login link, no full nav bar).

### Landing Page

- Hero section: large Crimson Pro heading ("Find Your Place in the Story"), subtitle, centered
- 3-step "How it works" with numbered circles (`--brown-dark` bg, `--gold` number)
- Single "Log In" primary button
- Note: "Registration is by invite only"
- No signup button (invite-only system)

### Login Page

- Centered form card (max-width 400px)
- Decorative `*` above title
- Email/password fields + "Log In" button
- Social auth buttons (Google, Discord, Facebook) below a divider
- "Registration is by invite only" note at bottom

### Join Page (Invite Claim)

- **Casting preview card** at top: shows run name, character name, house badge, year badge, role/path/blood status. Centered, with decorative divider.
- **Signup form** below (for unauthenticated): email, password, confirm password, "Join as [Character Name]" button, social auth options, link to login
- **Confirm button** (for authenticated): just the casting preview + confirm button

### Run List Page

- Extends `base.html`, uses full nav
- "My Runs" heading centered, Crimson Pro
- Each run displayed as a card: run name as a link (Crimson Pro heading), character name + role/house/year/path info, optional date range muted below
- Empty state: parchment-toned message with invite instructions

### Profile Page

- Centered form (max-width 500px)
- Fields: contact email, Discord username, Facebook URL, Instagram URL
- Helper text under contact email
- Save button

### Message Board (Feed)

- **CTA banner** (if no post yet): dashed border, centered text + "Write Introduction" button
- **Post cards** in chronological order, separated by decorative dividers
- Each card shows:
  - Role tab (top-left)
  - House-colored top border
  - Character name (Crimson Pro, large) with house badge + year badge inline
  - Keyword chips
  - **Preview content** (player-configurable, default: rumor):
    - Rumor mode: one italic rumor with curly quotes and left border
    - Looking-for mode: "Looking for:" label + looking-for label chips
    - Bio mode: truncated description text
  - **Photo tiles** (Facebook-style, see Photo Tiling below)
  - "Read more about [Name]" link
- Pagination at bottom

### Post Detail

- Back link at top
- Full detail card with:
  - Role tab + house top border
  - Character header: portrait (140x140, rounded) + name/badges/meta
  - Photo gallery (Facebook-style tiling, larger than feed)
  - Decorative divider
  - **Character bio** (shown first by default; player can configure order)
  - Decorative divider
  - **Looking For** items: each in a sub-card with label (Crimson Pro semibold) + description
  - Decorative divider
  - **Rumors**: italic Crimson Pro, left-bordered, tinted background
  - Decorative divider
  - **Contact** info: email + Discord inline
- **Comments section** below the detail card, in its own bordered container
- **Edit/Delete** buttons (visible to post author only)

Note: The display order of bio vs rumors vs looking-for sections should be a player preference. Default: bio first. This is a future model field on the post or user profile.

### Discover: Faculty

- Title + subtitle, centered
- **Grid of cards** (auto-fill, min 200px): portrait area (full-width, 180px tall) + info below
- Each card: portrait, name (Crimson Pro), subject (italic), house monitor dot + label
- **Ordering:** headmaster first, then professors, then staff. No separate section headings.
- Faculty cards: professors who monitor a house use that house's color for the top border; other professors and staff use gold (`--gold-dark`); headmaster uses `--brown-dark`

### Discover: Students

- Title + subtitle, centered
- **Two-column layout:** filter sidebar (220px) + results
- **Filter sidebar:** search input, dropdowns for house/year/path/club/blood status, keyword text input. All submit via HTMX.
- **"Someone you might meet in the hallways" widget** at top of results: dashed border, italic title, one random student card inside. Refreshes on page load.
- **Student result cards** (compact): small thumbnail (64x64), name + house badge + year/path, rumor or looking-for preview, keyword chips, "Read more" link
- Result count shown above cards

### Discover: Other

- Filterable by category
- Same card style as feed but for "other" post type

### Post Form (Character Introduction)

- Centered (max-width 70ch)
- **Read-only casting info** box at top: grid of role/house/year/path from casting, tinted background
- Form fields in a card:
  - Character name (text input)
  - Blood status + clubs (side-by-side dropdowns)
  - About (textarea/rich text)
  - Keywords (tag input with chips, autocomplete from global pool)
  - Decorative divider
  - Looking For (repeatable: label input + description input, "+ Add" button)
  - Decorative divider
  - Rumors (repeatable: italic text areas with left border styling, "+ Add Rumor" button)
  - Decorative divider
  - Photos (existing photo grid with "Remove" checkboxes + drag-to-upload area)
  - Publish + Cancel buttons

## Photo Tiling (Facebook-style)

Feed cards and detail views display photos in a tiled grid rather than a single portrait. Layout templates by photo count:

| Count | Grid | Behavior |
|---|---|---|
| 1 | Single image, constrained width (280px feed / larger in detail) | — |
| 2 | Two equal columns, single row | — |
| 3 | 2:1 ratio — main image spans 2 rows, 2 smaller images stacked right | — |
| 4+ | Same as 3-photo layout; last visible cell shows "+N more" overlay | Overlay: semi-transparent dark with count text |

- Feed tiles: ~120px row height, max-width 420px
- Detail tiles: ~160px row height, larger
- 4px gap between tiles, 6px border-radius, `--gold-muted` border
- Placeholder (no photo): gradient background with person silhouette SVG icon
- **Implementation:** Template-driven — the template checks photo count and outputs a different HTML structure per layout (CSS classes `photo-grid--1`, `photo-grid--2`, `photo-grid--3`, `photo-grid--4plus`). CSS handles the grid sizing, not the count logic.

## CSS Architecture

- **Remove Pico CSS** from player-facing templates
- **Create `static/css/player.css`** — single custom stylesheet for all player pages
- CSS custom properties (variables) for the palette, defined in `:root`
- No CSS framework dependency; vanilla CSS with flexbox/grid
- **Dashboard keeps Pico CSS** — only add shared Google Fonts link and warm accent overrides for brand consistency
- Responsive: single-column on mobile, student discover sidebar collapses to above-content on narrow screens
- **Breakpoints:** `768px` (sidebar collapses, nav stacks), `480px` (smaller text adjustments, photo grids simplify to single column)
- **Target browsers:** last 2 versions of Chrome, Firefox, Safari, Edge. No IE11 support.
- Tom Select: add minimal CSS overrides in `player.css` to match input styling (border color, border-radius, font family)

## Per-Run Color Overrides

Organizers can customize a run's color scheme to match their event's branding. A small set of fields on the `Run` model drives the theming — not every token, just the ones that define the visual identity.

### Model Fields (on `Run`)

| Field | Type | Default | Maps to |
|---|---|---|---|
| `theme_accent` | CharField(max_length=7, blank=True) | `""` (uses `--gold`) | `--gold`, `--gold-muted` (derived), `--gold-dark` (derived) |
| `theme_nav_bg` | CharField(max_length=7, blank=True) | `""` (uses `--brown-dark`) | `--brown-dark`, `--brown-mid` (derived) |
| `theme_page_bg` | CharField(max_length=7, blank=True) | `""` (uses `--parchment-light`) | `--parchment-light`, `--parchment-dark` (derived) |
| `theme_text` | CharField(max_length=7, blank=True) | `""` (uses `--ink`) | `--ink` |

All fields are optional hex color strings (e.g. `#c4a265`). Empty means "use default."

### Derivation

From each base color, related tokens are derived automatically (e.g. accent color generates muted and dark variants by adjusting lightness). This keeps the organizer-facing UI simple (4 color pickers) while maintaining palette coherence. Derivation happens in a template tag or context processor — not in CSS.

### Template Integration

The player `base.html` (and standalone pages) output an inline `<style>` block before the `player.css` link when any theme field is set:

```html
{% if run.theme_accent or run.theme_nav_bg or run.theme_page_bg or run.theme_text %}
<style>
  :root {
    {% if run.theme_accent %}--gold: {{ run.theme_accent }};{% endif %}
    /* derived values set by template tag */
  }
</style>
{% endif %}
```

This overrides the `player.css` defaults. Dark mode derivation adjusts automatically from the same base colors.

### Dashboard UI

Add a "Theme" section to the run settings page with 4 color picker inputs. Preview swatch next to each. No live preview in v1 — organizer saves and checks the player-facing side.

## Dark Mode

A "candlelit study" dark mode — same warm palette inverted, not a generic cold dark theme. Toggled via `prefers-color-scheme: dark` media query (follows OS setting). No manual toggle in v1.

### Dark Palette (CSS custom property overrides)

| Token | Light | Dark | Notes |
|---|---|---|---|
| `--parchment-light` | `#f5e6c8` | `#1e1a14` | Deep warm brown, not pure black |
| `--parchment-dark` | `#e8d5a8` | `#252015` | Gradient end |
| `--ink` | `#2c1810` | `#e8d5a8` | Parchment-toned text, not pure white |
| `--ink-light` | `#5c3d2e` | `#c4a265` | Warmer secondary text |
| `--gold` | `#d4a547` | `#d4a547` | Unchanged — already pops on dark |
| `--gold-muted` | `#c4a265` | `#5a4a30` | Muted borders, less prominent |
| `--gold-dark` | `#6b5311` | `#d4a547` | Links brighter on dark bg |
| `--brown-dark` | `#3d2b1f` | `#1a1410` | Nav background deepens |
| `--brown-mid` | `#5c3d2e` | `#2a2018` | Nav gradient end |
| `--brown-muted` | `#8b6f4e` | `#8b6f3a` | Slightly warmer muted |
| `--card-bg` | `rgba(255,255,255,0.45)` | `rgba(255,255,255,0.06)` | Very subtle lift |
| `--card-bg-hover` | `rgba(255,255,255,0.55)` | `rgba(255,255,255,0.10)` | Subtle hover |
| `--error` | `#8b3a3a` | `#d46a6a` | Brighter on dark |
| `--success` | `#3a6b3a` | `#6ad46a` | Brighter on dark |

### Implementation

All dark mode values are CSS custom property overrides inside a `@media (prefers-color-scheme: dark)` block in `player.css`. No separate stylesheet, no JS toggle. Components use the same CSS property names — only the values change.

### Key Adaptations

- **Primary button inverts:** gold background (`--gold`) with dark text (`--parchment-light`) instead of dark bg with gold text. Stands out better on dark surfaces.
- **Nav border:** uses `--gold-muted` (the muted dark value `#8b6f3a`), subtler than light mode.
- **House badges:** keep house background color, but text becomes `--parchment-dark` (light) for readability on dark page.
- **Photo placeholders:** gradient backgrounds darken further; SVG strokes use muted gold.
- **"+N more" overlay:** darker overlay (`rgba(30,26,20,0.65)`) with gold text.
- **Chip backgrounds:** `rgba(139,111,58,0.25)` — warm-tinted translucent instead of light-tinted.

## What Stays the Same

- HTMX interactions (expand posts, filter submission, comment threading, autocomplete)
- All existing URL structure and view logic
- Template structure (base.html, partials in `partials/`)
- Dashboard templates and styling (Pico CSS)
- All backend models and views

## Out of Scope

- Player-configurable feed preview mode (rumor/looking-for/bio) — noted for future, not implemented in this pass. Default to rumor with looking-for fallback.
- Player-configurable detail section order — noted for future. Default to bio first.
- Manual dark mode toggle (v1 follows OS `prefers-color-scheme` only)
- Animations beyond simple hover transitions
- Mobile-specific hamburger menu (nav wraps naturally)
