# Fantasy Theming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Pico CSS on player-facing pages with a custom "Enchanted Parchment" fantasy theme, including dark mode and per-run color overrides.

**Architecture:** Single `static/css/player.css` stylesheet with CSS custom properties for the full palette. Templates reworked for semantic class names. Per-run overrides via inline `<style>` block from Run model fields. Dark mode via `@media (prefers-color-scheme: dark)` variable overrides.

**Tech Stack:** Django templates, vanilla CSS (flexbox/grid), Google Fonts (Crimson Pro + Source Sans 3), HTMX (unchanged)

**Spec:** `docs/superpowers/specs/2026-04-06-fantasy-theming-design.md`

---

## File Map

### New Files

| File | Responsibility |
|---|---|
| `static/css/player.css` | Full player-facing stylesheet: variables, reset, typography, layout, nav, cards, badges, chips, buttons, forms, dividers, photo grid, comments, flash messages, dark mode, responsive, Tom Select overrides |
| `runs/migrations/NNNN_add_theme_fields.py` | Migration adding 4 theme CharFields to Run |
| `posts/templatetags/theme_tags.py` | Template tag `{% theme_vars run %}` that outputs inline `<style>` with per-run CSS variable overrides |
| `posts/templatetags/photo_grid.py` | Template inclusion tag `{% photo_grid photos size %}` that renders the correct tiling layout by photo count |
| `templates/player/partials/_photo_grid.html` | Photo grid partial template used by the `photo_grid` inclusion tag |

### Modified Files

| File | What Changes |
|---|---|
| `runs/models.py:73-95` | Add 4 theme fields to Run model |
| `templates/player/base.html` | Replace Pico CSS with player.css + Google Fonts, rework nav, add theme_vars tag, restyle flash messages and rumor banner |
| `templates/player/landing.html` | Replace Pico CSS with player.css, rework to fantasy landing page |
| `templates/player/login.html` | Replace Pico CSS with player.css, rework to fantasy login page |
| `templates/player/join.html` | Replace Pico CSS with player.css, rework to fantasy join page with casting preview card |
| `templates/player/run_list.html` | Rework from Pico `<article>` tags to themed run cards |
| `templates/player/profile.html` | Restyle form with fantasy form card |
| `templates/player/message_board.html` | Add CTA banner, decorative dividers, themed pagination |
| `templates/player/post_detail.html` | Rework to detail card with header, gallery, sections, themed comments, edit/delete buttons |
| `templates/player/post_form.html` | Restyle casting info box, form fields, keyword/LF/rumor/photo sections |
| `templates/player/discover/faculty.html` | Rework to themed faculty grid with portrait areas |
| `templates/player/discover/students.html` | Restyle sidebar and layout with themed classes |
| `templates/player/discover/other.html` | Restyle category filter and results |
| `templates/player/partials/_post_preview.html` | Rework to themed feed card with role tab, badges, rumor preview, photo tiles |
| `templates/player/partials/_post_content.html` | Rework to themed detail sections (bio, looking-for, rumors, contact, gallery) |
| `templates/player/partials/_post_expanded.html` | Update classes to match new theme |
| `templates/player/partials/_post_card_faculty.html` | Rework to themed faculty card with portrait area |
| `templates/player/partials/_student_results.html` | Rework to compact themed student cards with thumbnails |
| `templates/player/partials/_hallway_widget.html` | Restyle with dashed border, italic title, themed student card |
| `templates/player/partials/_other_results.html` | Restyle to themed card list |
| `templates/player/partials/_rumor_banner.html` | Restyle as ambient centered italic text with `aria-hidden` |
| `templates/player/partials/_comment_thread.html` | Restyle with gold borders, Crimson Pro author names |
| `templates/player/partials/_comment_form.html` | Restyle with themed input and button |
| `dashboard/forms/run.py` | Add theme fields to RunSettingsForm |
| `templates/dashboard/run_settings.html` | Add color picker inputs for theme fields |

---

## Task 1: Create `player.css` — Variables, Reset, Typography, Layout

**Files:**
- Create: `static/css/player.css`

This is the foundation. Everything else builds on these variables and base styles.

- [ ] **Step 1: Create the CSS file with custom properties and reset**

```css
/* static/css/player.css */

/* ===== Custom Properties ===== */
:root {
  --parchment-light: #f5e6c8;
  --parchment-dark: #e8d5a8;
  --ink: #2c1810;
  --ink-light: #5c3d2e;
  --gold: #d4a547;
  --gold-muted: #c4a265;
  --gold-dark: #6b5311;
  --brown-dark: #3d2b1f;
  --brown-mid: #5c3d2e;
  --brown-muted: #8b6f4e;
  --card-bg: rgba(255,255,255,0.45);
  --card-bg-hover: rgba(255,255,255,0.55);
  --error: #8b3a3a;
  --success: #3a6b3a;
}

/* ===== Reset ===== */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Source Sans 3', 'Segoe UI', sans-serif;
  color: var(--ink);
  background: linear-gradient(135deg, var(--parchment-light), var(--parchment-dark));
  min-height: 100vh;
  line-height: 1.6;
}
h1, h2, h3, h4, h5, h6 {
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--ink);
  line-height: 1.3;
}
a { color: var(--gold-dark); text-decoration: none; }
a:hover { text-decoration: underline; }
img { max-width: 100%; height: auto; }

/* ===== Layout ===== */
.page-container { max-width: 900px; margin: 0 auto; padding: 0 24px; }
.content-container { max-width: 70ch; margin: 0 auto; width: 100%; }
.page-body { padding: 24px; }
.page-center { text-align: center; }

/* ===== Typography Utilities ===== */
.font-serif { font-family: 'Crimson Pro', Georgia, serif; }
.text-muted { color: var(--brown-muted); }
.text-error { color: var(--error); }
.text-small { font-size: 0.85em; }
```

- [ ] **Step 2: Add component styles — nav, buttons, forms, cards, badges, chips, dividers**

```css
/* ===== Navigation ===== */
.nav {
  background: linear-gradient(180deg, var(--brown-dark), var(--brown-mid));
  padding: 12px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-family: 'Crimson Pro', Georgia, serif;
  border-bottom: 3px solid var(--gold-muted);
  flex-wrap: wrap;
  gap: 8px;
}
.nav-brand {
  font-size: 1.3em;
  color: var(--gold);
  letter-spacing: 0.06em;
  text-decoration: none;
}
.nav-brand:hover { text-decoration: none; }
.nav-links {
  font-size: 0.9em;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.nav-links a { color: var(--gold-muted); text-decoration: none; }
.nav-links a:hover { color: var(--gold); }
.nav-links a.active { color: var(--gold); }
.nav-links .nav-muted { color: var(--brown-muted); }
.nav-links .nav-sep { color: var(--brown-muted); }

/* ===== Buttons ===== */
.btn-primary {
  display: inline-block;
  background: var(--brown-dark);
  color: var(--gold);
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 0.95em;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}
.btn-primary:hover { opacity: 0.9; text-decoration: none; }
.btn-outline {
  display: inline-block;
  background: transparent;
  color: var(--ink-light);
  border: 1px solid var(--gold-muted);
  padding: 8px 18px;
  border-radius: 6px;
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 0.95em;
  cursor: pointer;
  text-decoration: none;
  text-align: center;
}
.btn-outline:hover { background: var(--card-bg); text-decoration: none; }
.btn-danger {
  display: inline-block;
  background: transparent;
  color: var(--error);
  border: 1px solid var(--error);
  padding: 8px 18px;
  border-radius: 6px;
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 0.95em;
  cursor: pointer;
  text-decoration: none;
}
.btn-danger:hover { background: rgba(139,58,58,0.08); text-decoration: none; }

/* ===== Form Inputs ===== */
input[type="text"], input[type="email"], input[type="password"],
input[type="search"], input[type="url"], input[type="number"],
select, textarea {
  width: 100%;
  background: rgba(255,255,255,0.6);
  border: 1px solid var(--gold-muted);
  border-radius: 6px;
  padding: 8px 12px;
  font-family: 'Source Sans 3', sans-serif;
  font-size: 0.92em;
  color: var(--ink);
  outline: none;
  margin-bottom: 4px;
}
input:focus, select:focus, textarea:focus {
  border-color: var(--gold);
  box-shadow: 0 0 0 2px rgba(212,165,71,0.2);
}
label {
  display: block;
  font-size: 0.85em;
  color: var(--ink-light);
  font-family: 'Crimson Pro', Georgia, serif;
  margin-bottom: 4px;
  margin-top: 12px;
}
label:first-child { margin-top: 0; }

/* ===== Cards ===== */
.card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 16px;
  position: relative;
}
.card-lg { padding: 24px; }
.card:hover { background: var(--card-bg-hover); }
.card-no-hover:hover { background: var(--card-bg); }

/* ===== Role Tab ===== */
.role-tab {
  position: absolute;
  top: -1px;
  left: 14px;
  color: var(--parchment-light);
  font-size: 0.6em;
  padding: 1px 8px;
  border-radius: 0 0 4px 4px;
  font-family: 'Crimson Pro', Georgia, serif;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

/* ===== Badges ===== */
.house-badge {
  display: inline-block;
  color: var(--parchment-light);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.55em;
  vertical-align: middle;
  text-decoration: none;
}
.house-badge:hover { text-decoration: none; opacity: 0.9; }
.year-badge {
  display: inline-block;
  border-width: 2px;
  border-style: solid;
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 0.55em;
  vertical-align: middle;
  color: var(--ink-light);
  text-decoration: none;
}
.year-badge:hover { text-decoration: none; }

/* ===== Chips ===== */
.chip {
  display: inline-block;
  background: rgba(196,146,101,0.3);
  border: 1px solid var(--gold-muted);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75em;
  color: var(--ink-light);
  text-decoration: none;
  margin: 2px 0;
}
.chip-keyword { cursor: pointer; }
.chip-keyword:hover { background: rgba(196,146,101,0.5); text-decoration: none; }
.chip-sm { font-size: 0.72em; padding: 1px 6px; border-radius: 8px; }
.chip-lf {
  background: rgba(139,105,20,0.12);
  border: 1px solid var(--gold-muted);
}

/* ===== Dividers ===== */
.divider {
  text-align: center;
  color: var(--gold-muted);
  letter-spacing: 0.3em;
  margin: 14px 0;
  font-size: 0.85em;
}
.divider-lg { font-size: 1em; margin: 4px 0 14px; }

/* ===== Rumor (in feed) ===== */
.rumor-preview {
  font-family: 'Crimson Pro', Georgia, serif;
  font-style: italic;
  color: var(--ink-light);
  font-size: 0.92em;
  line-height: 1.55;
  margin: 10px 0 6px;
  padding-left: 14px;
  border-left: 2px solid var(--gold-muted);
}
.rumor-preview::before { content: '\201C'; color: var(--gold-muted); font-size: 1.2em; margin-right: 2px; }
.rumor-preview::after { content: '\201D'; color: var(--gold-muted); font-size: 1.2em; margin-left: 2px; }

/* ===== Rumor (in detail) ===== */
.rumor-detail {
  font-family: 'Crimson Pro', Georgia, serif;
  font-style: italic;
  color: var(--ink-light);
  font-size: 0.92em;
  line-height: 1.55;
  padding: 10px 14px;
  margin-bottom: 6px;
  background: rgba(196,162,101,0.1);
  border-left: 3px solid var(--gold-muted);
  border-radius: 0 6px 6px 0;
}

/* ===== Flash Messages ===== */
.flash {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 12px;
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-left-width: 4px;
}
.flash-success { border-left-color: var(--success); color: var(--success); }
.flash-error { border-left-color: var(--error); color: var(--error); }
.flash-info { border-left-color: var(--gold-dark); color: var(--ink-light); }
.flash-warning { border-left-color: var(--gold); color: var(--ink-light); }

/* ===== Form Card ===== */
.form-card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 10px;
  padding: 28px;
}
.form-title {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.4em;
  color: var(--brown-dark);
  text-align: center;
  margin-bottom: 16px;
}

/* ===== Section Title ===== */
.section-title {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.15em;
  color: var(--ink-light);
  margin-bottom: 8px;
  letter-spacing: 0.03em;
}

/* ===== Back Link ===== */
.back-link {
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--gold-dark);
  font-size: 0.9em;
  text-decoration: none;
  border-bottom: 1px dotted var(--gold-muted);
  display: inline-block;
  margin-bottom: 14px;
}
.back-link:hover { text-decoration: none; border-bottom-style: solid; }

/* ===== Read More Link ===== */
.read-more {
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--gold-dark);
  font-size: 0.85em;
  text-decoration: none;
  border-bottom: 1px dotted var(--gold-muted);
  cursor: pointer;
}
.read-more:hover { border-bottom-style: solid; text-decoration: none; }

/* ===== Comments ===== */
.comment {
  border-left: 2px solid var(--gold-muted);
  padding: 10px 0 10px 14px;
  margin-bottom: 8px;
}
.comment-nested { margin-left: 24px; }
.comment-author {
  font-family: 'Crimson Pro', Georgia, serif;
  font-weight: 600;
  color: var(--ink-light);
  font-size: 0.9em;
}
.comment-time { font-size: 0.75em; color: var(--brown-muted); margin-left: 8px; }
.comment-body { font-size: 0.88em; color: var(--ink); line-height: 1.55; margin-top: 4px; }
.comment-actions { font-size: 0.78em; color: var(--gold-dark); margin-top: 4px; }

/* ===== CTA Banner ===== */
.cta-banner {
  background: rgba(61,43,31,0.08);
  border: 1px dashed var(--gold-muted);
  border-radius: 8px;
  padding: 14px;
  text-align: center;
  margin-bottom: 16px;
}
.cta-banner .font-serif { color: var(--ink-light); font-size: 1.1em; }

/* ===== Rumor Banner (ambient, base template) ===== */
.rumor-banner {
  text-align: center;
  padding: 8px 16px;
  font-family: 'Crimson Pro', Georgia, serif;
  font-style: italic;
  font-size: 0.9em;
  color: var(--ink-light);
  opacity: 0.75;
}
.rumor-banner a { color: var(--gold-dark); }

/* ===== Hallway Widget ===== */
.hallway-widget {
  background: rgba(139,105,20,0.08);
  border: 1px dashed var(--gold-muted);
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 16px;
  text-align: center;
}
.hallway-title {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 0.95em;
  color: var(--gold-dark);
  font-style: italic;
  margin-bottom: 8px;
}

/* ===== Footer ===== */
.site-footer {
  text-align: center;
  padding: 24px;
  font-size: 0.85em;
  color: var(--brown-muted);
}

/* ===== Contact Row ===== */
.contact-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 0.85em;
  color: var(--ink-light);
  margin-top: 4px;
}
.contact-item { display: flex; align-items: center; gap: 4px; }

/* ===== Looking For Items ===== */
.lf-item {
  background: rgba(255,255,255,0.4);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 12px 14px;
  margin-bottom: 8px;
}
.lf-label {
  font-family: 'Crimson Pro', Georgia, serif;
  font-weight: 600;
  color: var(--ink-light);
  font-size: 1em;
}
.lf-desc { font-size: 0.88em; color: var(--ink); line-height: 1.55; margin-top: 4px; }

/* ===== Social Auth Buttons ===== */
.btn-social {
  width: 100%;
  background: rgba(255,255,255,0.5);
  border: 1px solid var(--gold-muted);
  border-radius: 6px;
  padding: 8px;
  font-family: 'Source Sans 3', sans-serif;
  font-size: 0.88em;
  color: var(--brown-dark);
  cursor: pointer;
  margin-bottom: 8px;
  text-align: center;
  display: block;
  text-decoration: none;
}
.btn-social:hover { background: rgba(255,255,255,0.7); text-decoration: none; }

/* ===== Divider with Text ===== */
.divider-text {
  text-align: center;
  color: var(--brown-muted);
  font-size: 0.82em;
  margin: 14px 0;
  position: relative;
}
.divider-text::before, .divider-text::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1px;
  background: var(--gold-muted);
}
.divider-text::before { left: 0; }
.divider-text::after { right: 0; }

/* ===== Small Link ===== */
.small-link {
  font-size: 0.85em;
  color: var(--gold-dark);
  text-decoration: none;
  border-bottom: 1px dotted var(--gold-muted);
}
.small-link:hover { border-bottom-style: solid; text-decoration: none; }
```

- [ ] **Step 3: Add photo grid, faculty grid, student layout, and responsive styles**

```css
/* ===== Photo Grid ===== */
.photo-grid {
  display: grid;
  gap: 4px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--gold-muted);
  margin-top: 10px;
}
.photo-grid img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-grid--1 { grid-template-columns: 1fr; grid-template-rows: 160px; max-width: 280px; }
.photo-grid--2 { grid-template-columns: 1fr 1fr; grid-template-rows: 140px; max-width: 420px; }
.photo-grid--3 { grid-template-columns: 2fr 1fr; grid-template-rows: 120px 120px; max-width: 420px; }
.photo-grid--3 .photo-main { grid-row: 1 / 3; }
.photo-grid--4plus { grid-template-columns: 2fr 1fr; grid-template-rows: 120px 120px; max-width: 420px; }
.photo-grid--4plus .photo-main { grid-row: 1 / 3; }
.photo-more {
  position: relative;
}
.photo-more::after {
  content: attr(data-more);
  position: absolute;
  inset: 0;
  background: rgba(44,24,16,0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--parchment-dark);
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 0.95em;
}

/* Detail page uses larger tiles */
.photo-grid-detail .photo-grid--1 { grid-template-rows: 220px; max-width: 400px; }
.photo-grid-detail .photo-grid--2 { grid-template-rows: 180px; }
.photo-grid-detail .photo-grid--3 { grid-template-rows: 160px 160px; }
.photo-grid-detail .photo-grid--4plus { grid-template-rows: 160px 160px; }

/* ===== Faculty Grid ===== */
.faculty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  max-width: 860px;
  margin: 0 auto;
}
.faculty-card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  color: inherit;
  transition: box-shadow 0.2s;
}
.faculty-card:hover { box-shadow: 0 4px 16px rgba(139,105,20,0.25); text-decoration: none; }
.faculty-portrait {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.faculty-portrait img { width: 100%; height: 100%; object-fit: cover; }
.faculty-info { padding: 12px; }
.faculty-name {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.1em;
  font-weight: 600;
  color: var(--ink);
}
.faculty-subject {
  font-size: 0.85em;
  color: var(--gold-dark);
  font-style: italic;
  font-family: 'Crimson Pro', Georgia, serif;
  margin: 2px 0;
}
.faculty-meta { font-size: 0.78em; color: var(--brown-muted); margin-top: 4px; }
.faculty-house-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  vertical-align: middle;
  margin-right: 3px;
}

/* ===== Student Discover Layout ===== */
.student-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 20px;
  max-width: 860px;
  margin: 0 auto;
}
.filter-sidebar {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 16px;
  align-self: start;
}
.filter-title {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1em;
  color: var(--ink-light);
  margin-bottom: 10px;
}

/* ===== Student Card (compact) ===== */
.student-card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 8px;
  position: relative;
  display: flex;
  gap: 12px;
}
.student-card:hover { background: var(--card-bg-hover); }
.student-thumb {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  border: 1.5px solid var(--gold-muted);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-top: 6px;
}
.student-thumb img { width: 100%; height: 100%; object-fit: cover; }
.student-name {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.05em;
  font-weight: 600;
  color: var(--ink);
  margin-top: 6px;
}

/* ===== Post Feed Card ===== */
.post-card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 16px;
  position: relative;
  margin-bottom: 6px;
}
.post-card:hover { background: var(--card-bg-hover); }
.post-name {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.25em;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 2px;
}

/* ===== Detail Card ===== */
.detail-card { padding: 24px; }
.char-header { display: flex; gap: 20px; margin-top: 10px; margin-bottom: 16px; }
.char-portrait {
  width: 140px;
  height: 140px;
  border-radius: 10px;
  border: 2px solid var(--gold-muted);
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}
.char-portrait img { width: 100%; height: 100%; object-fit: cover; }
.char-name {
  font-family: 'Crimson Pro', Georgia, serif;
  font-size: 1.6em;
  font-weight: 600;
  color: var(--ink);
  margin-bottom: 6px;
}
.meta-row { font-size: 0.9em; color: var(--ink-light); margin: 4px 0; }
.meta-label {
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--gold-dark);
}

/* ===== Description ===== */
.description {
  font-size: 0.95em;
  color: var(--ink);
  line-height: 1.7;
  margin-bottom: 16px;
}

/* ===== Casting Info (read-only box in post form) ===== */
.casting-info {
  background: rgba(139,105,20,0.08);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}
.casting-info-title {
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--ink-light);
  font-size: 0.95em;
  margin-bottom: 8px;
  font-weight: 600;
}
.casting-grid {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 4px 16px;
  font-size: 0.88em;
}
.casting-grid .label { color: var(--brown-muted); font-family: 'Crimson Pro', Georgia, serif; }
.casting-grid .value { color: var(--ink); }

/* ===== Pagination ===== */
.pagination {
  text-align: center;
  margin-top: 20px;
  font-family: 'Crimson Pro', Georgia, serif;
  color: var(--brown-muted);
  font-size: 0.95em;
}
.pagination a { color: var(--gold-dark); margin: 0 8px; }

/* ===== Steps (landing page) ===== */
.steps { display: flex; gap: 24px; justify-content: center; flex-wrap: wrap; margin-bottom: 32px; }
.step { width: 150px; text-align: center; }
.step-number {
  width: 44px; height: 44px; border-radius: 50%;
  background: var(--brown-dark); color: var(--gold);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 8px;
  font-family: 'Crimson Pro', Georgia, serif; font-size: 1.2em;
}
.step-title { font-family: 'Crimson Pro', Georgia, serif; color: var(--ink-light); font-size: 0.95em; font-weight: 600; }
.step-desc { font-size: 0.8em; color: var(--brown-muted); margin-top: 4px; }

/* ===== Run Card (run list page) ===== */
.run-card {
  background: var(--card-bg);
  border: 1px solid var(--gold-muted);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 12px;
}
.run-card:hover { background: var(--card-bg-hover); }
.run-card h3 {
  font-family: 'Crimson Pro', Georgia, serif;
  margin-bottom: 4px;
}
.run-card h3 a { color: var(--ink); }
.run-card h3 a:hover { color: var(--gold-dark); }

/* ===== Tom Select Overrides ===== */
.ts-wrapper .ts-control {
  background: rgba(255,255,255,0.6) !important;
  border: 1px solid var(--gold-muted) !important;
  border-radius: 6px !important;
  font-family: 'Source Sans 3', sans-serif !important;
  color: var(--ink) !important;
}
.ts-wrapper .ts-dropdown {
  border: 1px solid var(--gold-muted) !important;
  border-radius: 6px !important;
}

/* ===== Responsive ===== */
@media (max-width: 768px) {
  .student-layout { grid-template-columns: 1fr; }
  .filter-sidebar { margin-bottom: 16px; }
  .nav { padding: 12px 16px; }
  .char-header { flex-direction: column; align-items: center; text-align: center; }
  .char-portrait { width: 120px; height: 120px; }
  .faculty-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 12px; }
}
@media (max-width: 480px) {
  .photo-grid--2, .photo-grid--3, .photo-grid--4plus {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  .photo-grid--3 .photo-main, .photo-grid--4plus .photo-main { grid-row: auto; }
  .steps { flex-direction: column; align-items: center; }
}
```

- [ ] **Step 4: Add dark mode**

```css
/* ===== Dark Mode ===== */
@media (prefers-color-scheme: dark) {
  :root {
    --parchment-light: #1e1a14;
    --parchment-dark: #252015;
    --ink: #e8d5a8;
    --ink-light: #c4a265;
    --gold: #d4a547;
    --gold-muted: #5a4a30;
    --gold-dark: #d4a547;
    --brown-dark: #1a1410;
    --brown-mid: #2a2018;
    --brown-muted: #8b6f3a;
    --card-bg: rgba(255,255,255,0.06);
    --card-bg-hover: rgba(255,255,255,0.10);
    --error: #d46a6a;
    --success: #6ad46a;
  }
  .btn-primary { background: var(--gold); color: var(--parchment-light); }
  .house-badge { color: var(--parchment-dark); }
  .chip { background: rgba(139,111,58,0.25); color: var(--ink-light); border-color: var(--gold-muted); }
  .photo-more::after { background: rgba(30,26,20,0.65); color: var(--gold); }
  .btn-social { background: rgba(255,255,255,0.08); color: var(--ink); border-color: var(--gold-muted); }
  .cta-banner { background: rgba(212,165,71,0.06); }
}
```

- [ ] **Step 5: Create directory and verify the file loads**

Run: `mkdir -p static/css` (directory does not yet exist)
Run: `.venv/bin/python manage.py collectstatic --dry-run --noinput 2>&1 | head -20`
Expected: lists `css/player.css` among files to collect (or no errors if STATICFILES_DIRS is configured)

- [ ] **Step 6: Commit**

```bash
git add static/css/player.css
git commit -m "Add player.css — full Enchanted Parchment theme with dark mode"
```

---

## Task 2: Per-Run Theme Fields on Run Model

**Files:**
- Modify: `runs/models.py:73-95`
- Create: `runs/migrations/NNNN_add_theme_fields.py` (auto-generated)
- Create: `posts/templatetags/theme_tags.py`

- [ ] **Step 1: Add theme fields to Run model**

In `runs/models.py`, add after the existing `blood_statuses` M2M field (line 89):

```python
    # Per-run theme color overrides (optional hex strings, e.g. "#c4a265")
    theme_accent = models.CharField(max_length=7, blank=True, default="", help_text="Accent color (gold)")
    theme_nav_bg = models.CharField(max_length=7, blank=True, default="", help_text="Navigation background")
    theme_page_bg = models.CharField(max_length=7, blank=True, default="", help_text="Page background")
    theme_text = models.CharField(max_length=7, blank=True, default="", help_text="Primary text color")
```

- [ ] **Step 2: Generate and run migration**

Run: `.venv/bin/python manage.py makemigrations runs -n add_theme_fields`
Run: `.venv/bin/python manage.py migrate`

- [ ] **Step 3: Create theme_tags template tag**

```python
# posts/templatetags/theme_tags.py
import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _is_valid_hex(value):
    return bool(value and _HEX_RE.match(value))


def _darken(hex_color, factor=0.7):
    """Darken a hex color by a factor (0-1)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color, factor=0.3):
    """Lighten a hex color by mixing with white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = r + int((255 - r) * factor)
    g = g + int((255 - g) * factor)
    b = b + int((255 - b) * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


@register.simple_tag
def theme_vars(run):
    """Output inline CSS custom property overrides for per-run theming.

    Validates hex format to prevent XSS via organizer-supplied color values.
    """
    if not run:
        return ""
    overrides = []
    if _is_valid_hex(run.theme_accent):
        overrides.append(f"--gold: {run.theme_accent}")
        overrides.append(f"--gold-muted: {_lighten(run.theme_accent, 0.3)}")
        overrides.append(f"--gold-dark: {_darken(run.theme_accent, 0.6)}")
    if _is_valid_hex(run.theme_nav_bg):
        overrides.append(f"--brown-dark: {run.theme_nav_bg}")
        overrides.append(f"--brown-mid: {_lighten(run.theme_nav_bg, 0.15)}")
    if _is_valid_hex(run.theme_page_bg):
        overrides.append(f"--parchment-light: {run.theme_page_bg}")
        overrides.append(f"--parchment-dark: {_darken(run.theme_page_bg, 0.9)}")
    if _is_valid_hex(run.theme_text):
        overrides.append(f"--ink: {run.theme_text}")
    if not overrides:
        return ""
    css = "; ".join(overrides)
    return mark_safe(f'<style>:root {{ {css} }}</style>')
```

- [ ] **Step 4: Verify template tag loads**

Run: `.venv/bin/python -c "from posts.templatetags.theme_tags import theme_vars; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add runs/models.py runs/migrations/ posts/templatetags/theme_tags.py
git commit -m "Add per-run theme fields and theme_vars template tag"
```

---

## Task 3: Create Photo Grid Template Tag

**Files:**
- Create: `posts/templatetags/photo_grid.py`

- [ ] **Step 1: Create the inclusion tag**

```python
# posts/templatetags/photo_grid.py
from django import template

register = template.Library()


@register.inclusion_tag("player/partials/_photo_grid.html")
def photo_grid(photos, size="feed"):
    """Render a Facebook-style photo grid.

    photos: queryset or list of Photo objects
    size: "feed" or "detail" (controls CSS sizing)
    """
    photo_list = list(photos) if photos else []
    count = len(photo_list)
    visible = photo_list[:3]
    extra = count - 3 if count > 3 else 0
    if count == 0:
        grid_class = ""
    elif count == 1:
        grid_class = "photo-grid--1"
    elif count == 2:
        grid_class = "photo-grid--2"
    elif count == 3:
        grid_class = "photo-grid--3"
    else:
        grid_class = "photo-grid--4plus"
    return {
        "photos": visible,
        "count": count,
        "extra": extra,
        "grid_class": grid_class,
        "size": size,
    }
```

- [ ] **Step 2: Create the photo grid partial template**

Create `templates/player/partials/_photo_grid.html`:

```html
{% if count > 0 %}
<div class="{% if size == 'detail' %}photo-grid-detail{% endif %}">
  <div class="photo-grid {{ grid_class }}">
    {% for photo in photos %}
      {% if forloop.first and count >= 3 %}
        <div class="photo-main">
          <img src="{{ photo.image.url }}" alt="{{ photo.caption }}">
        </div>
      {% elif forloop.last and extra > 0 %}
        <div class="photo-more" data-more="+{{ extra }} more" style="position:relative;overflow:hidden;">
          <img src="{{ photo.image.url }}" alt="{{ photo.caption }}">
        </div>
      {% else %}
        <div>
          <img src="{{ photo.image.url }}" alt="{{ photo.caption }}">
        </div>
      {% endif %}
    {% endfor %}
  </div>
</div>
{% endif %}
```

- [ ] **Step 3: Verify tag loads**

Run: `.venv/bin/python -c "from posts.templatetags.photo_grid import photo_grid; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add posts/templatetags/photo_grid.py templates/player/partials/_photo_grid.html
git commit -m "Add photo_grid template tag for Facebook-style photo tiling"
```

---

## Task 4: Rework `base.html` — Replace Pico with Fantasy Theme

**Files:**
- Modify: `templates/player/base.html`

This is the critical switch. All player pages that extend `base.html` will pick up the new theme.

- [ ] **Step 1: Rewrite base.html**

Replace the entire file with:

```html
{% load static post_tags theme_tags %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}LFR{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="{% static 'css/player.css' %}">
    {# theme_vars AFTER player.css so per-run overrides win by CSS cascade order #}
    {% if run %}{% theme_vars run %}{% endif %}
    <script src="https://unpkg.com/htmx.org@2.0.4"></script>
    {% block extra_head %}{% endblock %}
</head>
<body>
    <nav class="nav">
        <div>
            {% if run %}
            <a href="{% url 'posts:message_board' slug=run.slug %}" class="nav-brand">&#10022; {{ run.name }} &#10022;</a>
            {% else %}
            <a href="{% url 'runs:run_list' %}" class="nav-brand">&#10022; Looking for Relation &#10022;</a>
            {% endif %}
        </div>
        <div class="nav-links">
            {% if run %}
            <a href="{% url 'posts:message_board' slug=run.slug %}">Board</a>
            <span class="nav-sep">&bull;</span>
            <a href="{% url 'posts:discover_faculty' slug=run.slug %}">Faculty</a>
            <span class="nav-sep">&bull;</span>
            <a href="{% url 'posts:discover_students' slug=run.slug %}">Students</a>
            <span class="nav-sep">&bull;</span>
            <a href="{% url 'posts:discover_other' slug=run.slug %}">Other</a>
            <span class="nav-sep">&bull;</span>
            {% endif %}
            {% if user.is_authenticated %}
            <a href="{% url 'accounts:profile' %}">Profile</a>
            <span class="nav-sep">&bull;</span>
            <form method="post" action="{% url 'accounts:logout' %}" style="display:inline;margin:0;">
                {% csrf_token %}
                <button type="submit" class="nav-muted" style="background:none;border:none;cursor:pointer;font-family:'Crimson Pro',serif;font-size:inherit;color:var(--brown-muted);padding:0;">Logout</button>
            </form>
            {% endif %}
        </div>
    </nav>

    {% if run %}
    <div aria-hidden="true">
        {% random_rumor run %}
    </div>
    {% endif %}

    <main class="page-body">
        <div class="content-container">
            {% if messages %}
            {% for message in messages %}
            <div class="flash flash-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
            {% endif %}

            {% block content %}{% endblock %}
        </div>
    </main>

    <footer class="site-footer">
        LFR &mdash; Looking for Relation
    </footer>

    {% block extra_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Verify the page loads without errors**

Run: `.venv/bin/python manage.py check`
Expected: `System check identified no issues.`

- [ ] **Step 3: Commit**

```bash
git add templates/player/base.html
git commit -m "Replace Pico CSS with Enchanted Parchment theme in base.html"
```

---

## Task 5: Rework Standalone Pages (Landing, Login, Join)

**Files:**
- Modify: `templates/player/landing.html`
- Modify: `templates/player/login.html`
- Modify: `templates/player/join.html`

These don't extend `base.html` so they need their own CSS/font links.

- [ ] **Step 1: Rewrite landing.html**

Replace entire file — see spec "Landing Page" section. Key structure: `<head>` with Google Fonts + player.css, nav-simple with brand, hero section with heading/subtitle/steps/CTA button, footer.

- [ ] **Step 2: Rewrite login.html**

Replace entire file — see spec "Login Page" section. Key structure: `<head>` with Google Fonts + player.css, nav-simple, centered `form-card` (max-width 400px) with email/password, social auth as `btn-social` links, form errors in `--error` color.

- [ ] **Step 3: Rewrite join.html**

Replace entire file — see spec "Join Page" section. Key structure: `<head>` with Google Fonts + player.css, nav-simple, casting preview card with house badge/year badge, signup form or confirm button below, social auth, login link.

- [ ] **Step 4: Visually verify all three pages**

Open in browser: `/`, `/accounts/login/`, and a valid join URL.
Expected: Fantasy-themed pages with parchment background, Crimson Pro headings, gold accents.

- [ ] **Step 5: Commit**

```bash
git add templates/player/landing.html templates/player/login.html templates/player/join.html
git commit -m "Rework standalone pages (landing, login, join) with fantasy theme"
```

---

## Task 6: Rework Simple Pages (Run List, Profile)

**Files:**
- Modify: `templates/player/run_list.html`
- Modify: `templates/player/profile.html`

- [ ] **Step 1: Rewrite run_list.html**

Replace Pico `<article>` tags with `.run-card` divs. Each card: run name as `h3` link, character name + role/house/year/path as inline text, date range as `.text-muted` below.

- [ ] **Step 2: Rewrite profile.html**

Wrap form in a centered `.form-card` (max-width 500px). Replace `<button>` with `.btn-primary`. Use `.text-error` and `.text-muted` classes for field errors and help text. Add page title in Crimson Pro.

- [ ] **Step 3: Verify both pages**

Open in browser: `/runs/` and `/accounts/profile/`.

- [ ] **Step 4: Commit**

```bash
git add templates/player/run_list.html templates/player/profile.html
git commit -m "Rework run list and profile pages with fantasy theme"
```

---

## Task 7: Rework Feed — Message Board + Post Preview

**Files:**
- Modify: `templates/player/message_board.html`
- Modify: `templates/player/partials/_post_preview.html`
- Modify: `templates/player/partials/_rumor_banner.html`

- [ ] **Step 1: Rewrite message_board.html**

Replace content with: `.cta-banner` (if no character post), decorative divider, post loop with `_post_preview.html` partials separated by dividers, themed `.pagination` at bottom. Remove the "Edit My Character Post" / "New Post" button row — move these to the CTA or post detail.

- [ ] **Step 2: Rewrite _post_preview.html**

Each post becomes a `.post-card` with:
- `border-top: 3px solid` using house color (via `style` attribute from `post.casting.house.color`)
- `.role-tab` with role display, background color based on role
- `.post-name` with character name, inline `.house-badge` and `.year-badge`
- `.chip` elements for keywords
- Rumor preview (`.rumor-preview`) if post has rumors, else looking-for labels as `.chip-lf`, else truncated content
- `{% load photo_grid %}{% photo_grid post.photos.all "feed" %}` for photo tiles
- `.read-more` link to post detail

- [ ] **Step 3: Restyle _rumor_banner.html**

Update to use `.rumor-banner` class. Wrap rumor text in curly quotes. Keep existing template logic for character link.

- [ ] **Step 4: Verify feed page**

Open in browser: `/<run-slug>/`
Expected: Fantasy-themed feed with role tabs, house-colored borders, rumor previews, photo tiles.

- [ ] **Step 5: Commit**

```bash
git add templates/player/message_board.html templates/player/partials/_post_preview.html templates/player/partials/_rumor_banner.html
git commit -m "Rework message board feed with themed cards, rumor previews, photo tiles"
```

---

## Task 8: Rework Post Detail + Comments

**Files:**
- Modify: `templates/player/post_detail.html`
- Modify: `templates/player/partials/_post_content.html`
- Modify: `templates/player/partials/_post_expanded.html`
- Modify: `templates/player/partials/_comment_thread.html`
- Modify: `templates/player/partials/_comment_form.html`

- [ ] **Step 1: Rewrite post_detail.html**

Replace `<article>` with: `.back-link` at top, `.detail-card` with house top border, edit/delete as `.btn-outline` and `.btn-danger` below. Comments section in its own `.card` container.

- [ ] **Step 2: Rewrite _post_content.html**

**Important:** Add `{% load photo_grid %}` at the top of this partial. Add `aria-hidden="true"` to all decorative divider elements.

Full detail layout:
- `.char-header`: portrait (`.char-portrait` with first photo or placeholder) + name/badges/meta
- `{% photo_grid post.photos.all "detail" %}` for gallery
- Decorative divider (with `aria-hidden="true"`)
- `.section-title` "About [Name]" + `.description` with markdown content
- Divider + `.section-title` "Looking For" + `.lf-item` entries
- Divider + `.section-title` "What People Say" + `.rumor-detail` entries
- Divider + `.section-title` "Contact" + `.contact-row` with contact items

- [ ] **Step 3: Update _post_expanded.html**

Same as before but include `_post_content.html` and a "Full page" `.btn-outline` link.

- [ ] **Step 4: Rewrite _comment_thread.html**

Use `.comment` / `.comment-nested` classes. Author name as `.comment-author`, timestamp as `.comment-time`, body as `.comment-body`. Reply button as `.comment-actions` text link. Comment form textarea and submit use themed styles.

- [ ] **Step 5: Rewrite _comment_form.html**

Style the reply form textarea and button with theme classes.

- [ ] **Step 6: Verify post detail**

Open in browser: detail page for a post with photos, rumors, looking-for, and comments.

- [ ] **Step 7: Commit**

```bash
git add templates/player/post_detail.html templates/player/partials/_post_content.html templates/player/partials/_post_expanded.html templates/player/partials/_comment_thread.html templates/player/partials/_comment_form.html
git commit -m "Rework post detail and comments with fantasy theme"
```

---

## Task 9: Rework Discover Pages

**Files:**
- Modify: `templates/player/discover/faculty.html`
- Modify: `templates/player/discover/students.html`
- Modify: `templates/player/discover/other.html`
- Modify: `templates/player/partials/_post_card_faculty.html`
- Modify: `templates/player/partials/_student_results.html`
- Modify: `templates/player/partials/_hallway_widget.html`
- Modify: `templates/player/partials/_other_results.html`

- [ ] **Step 1: Rewrite faculty.html and _post_card_faculty.html**

**Important:** Add `aria-hidden="true"` to all decorative divider elements in these templates.

Page: centered title + subtitle, decorative divider, `.faculty-grid` wrapping faculty cards.
Each card (`.faculty-card`): `border-top` colored by monitor house or gold default, `.faculty-portrait` (full-width photo or initial placeholder), `.faculty-info` with name/subject/monitor.

Ordering: headmaster first, then professors, then staff (this may require a view change — check if the view already orders this way).

- [ ] **Step 2: Rewrite students.html, _student_results.html, _hallway_widget.html**

Page: centered title + subtitle, decorative divider, `.student-layout` grid with `.filter-sidebar` (left) and results (right). Sidebar uses `.filter-title`, themed selects and search input. Keep all existing HTMX attributes.

`_hallway_widget.html`: `.hallway-widget` with `.hallway-title`, themed `.student-card` inside with thumbnail, house badge, rumor preview, chips.

`_student_results.html`: Result count, then `.student-card` items with `.student-thumb`, `.student-name` + badges, rumor/looking-for preview, chips, `.read-more` link.

- [ ] **Step 3: Rewrite other.html and _other_results.html**

Page: centered title, themed category dropdown, results container.
Results: `.card` items with title link, category badge, timestamp, truncated content.

- [ ] **Step 4: Verify all discover pages**

Open in browser: faculty, students (try filters), and other pages.

- [ ] **Step 5: Commit**

```bash
git add templates/player/discover/ templates/player/partials/_post_card_faculty.html templates/player/partials/_student_results.html templates/player/partials/_hallway_widget.html templates/player/partials/_other_results.html
git commit -m "Rework discover pages (faculty, students, other) with fantasy theme"
```

---

## Task 10: Rework Post Form

**Files:**
- Modify: `templates/player/post_form.html`

- [ ] **Step 1: Rewrite post_form.html**

Replace content with:
- Centered page title in Crimson Pro
- Decorative divider
- `.casting-info` box (read-only) with `.casting-grid` for role/house/year/path
- `.form-card` containing all form fields with themed inputs
- Character name, blood status + clubs (side-by-side with CSS grid), content textarea
- Keywords input (Tom Select still loaded via CDN)
- Divider + Looking For section with themed row styling, "+ Add" button as dashed outline
- Divider + Rumors section with left-border italic styling, "+ Add Rumor" button
- Divider + Photos section with existing photo grid + upload area
- `.btn-primary` submit + `.btn-outline` cancel
- Form errors in `.text-error`

Keep all existing JS for Tom Select, addLookingForRow, addRumorRow — just update the generated HTML's class names in the JS functions.

- [ ] **Step 2: Verify post form**

Open in browser: create and edit character post forms.
Expected: Themed form with casting info box, proper input styling, Tom Select styled.

- [ ] **Step 3: Commit**

```bash
git add templates/player/post_form.html
git commit -m "Rework post form with fantasy theme"
```

---

## Task 11: Dashboard Theme Fields UI

**Files:**
- Modify: `dashboard/forms/run.py`
- Modify: `templates/dashboard/run_settings.html`

- [ ] **Step 1: Add theme fields to RunSettingsForm**

Check `dashboard/forms/run.py` for the `RunSettingsForm` and add `theme_accent`, `theme_nav_bg`, `theme_page_bg`, `theme_text` to its `Meta.fields`. Add `widgets` with `TextInput(attrs={"type": "color"})` for color picker rendering.

- [ ] **Step 2: Update run_settings.html**

Add a "Theme" fieldset/section grouping the 4 color fields. Use `<input type="color">` styling. Keep the existing form structure.

- [ ] **Step 3: Verify in dashboard**

Open in browser: run settings page. Set a custom accent color, save, check player-facing page.

- [ ] **Step 4: Commit**

```bash
git add dashboard/forms/run.py templates/dashboard/run_settings.html
git commit -m "Add per-run theme color pickers to dashboard settings"
```

---

## Task 12: Full Visual QA Pass

No code changes expected — this is a verification task.

- [ ] **Step 1: Check every page in light mode**

Visit: landing, login, join, run list, profile, message board, post detail, post form (create + edit), faculty, students (with filters), other. Check: fonts load, colors correct, badges/chips styled, photo grid works, comments threaded, flash messages styled.

- [ ] **Step 2: Check every page in dark mode**

Set OS to dark mode. Visit same pages. Check: backgrounds dark, text readable, buttons inverted, badges visible, photo overlay correct.

- [ ] **Step 3: Check responsive at 768px and 480px**

Resize browser. Check: sidebar collapses, nav wraps, photo grid simplifies, faculty grid reflows, char header stacks.

- [ ] **Step 4: Check per-run override**

Set a test run's `theme_accent` to a non-default color (e.g. `#3B82F6`). Verify the accent propagates to gold, buttons, borders.

- [ ] **Step 5: Run existing tests**

Run: `.venv/bin/python -m pytest --tb=short 2>&1`
Expected: All tests pass (template changes should not break functional tests).

- [ ] **Step 6: Fix any issues found, commit**

```bash
git add -A
git commit -m "Fix visual QA issues from fantasy theming"
```
