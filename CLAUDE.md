# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LFR (Looking for Relation)** — A web app for the Witchards LARP association to manage pre-game character relationship posts. Replaces the current workflow scattered across Facebook groups and Discord forums. Players post character descriptions, find housemates/classmates, and arrange pre-game relationships before LARP events (Czocha, Bothwell, etc.).

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** Django templates + HTMX (server-rendered with dynamic interactions — expanding posts, filter submission, comment threading, autocomplete via standalone JS libs like Tom Select)
- **API:** lightweight read-only JSON endpoints (or management commands) for one-time data export to an external logistics/tracking app (staff, players, props). No need for Django REST Framework — plain Django views returning JSON.

## Data Model

### Runs

A **run** is a single event (e.g. "College of Wizardry 23", "Bothwell 3"). Each run defines its own vocabulary — different events have different houses, paths, years, clubs, etc. Runs are created by admins.

A run configures:
- **First-class fields** (values are per-run, but the concepts are universal): houses, paths, years, clubs, teaching subjects, blood statuses
- **Custom attributes**: run-specific boolean/choice/text fields (e.g. "Prefect" for Czocha, "House Representative" for Bothwell, "Is Infected" for a zombie run). Each custom attribute specifies its type, allowed values, which roles it applies to, and whether it's filterable.

Example — Czocha run would define houses as [Libussa, Faust, Molin, Durentius, Sendivogius], years as [1st/Junior, 2nd/Sophomore, 3rd/Senior], and a "Prefect" boolean custom attribute (student-only, must be 3rd year).

Bothwell would define its own different set of houses, years (including a PhD-equivalent), and "House Representative" instead of "Prefect".

**Important:** The app is for the **pre-game LFR phase only**, not for use during the game itself. This affects the data model: juniors (1st years) do not have a house assigned during the LFR phase — house assignment happens at the in-game sorting ceremony. House is therefore nullable for students, and juniors are discovered via year, path, keywords, etc.

### Users and Auth

- **Email/password** authentication to start. Architecture should not block adding OAuth later (django-allauth).
- **Roles:** admin, organizer, player
  - **Admin:** creates and configures runs
  - **Organizer:** manages casting and invites for a run
  - **Player:** creates posts and comments

### Invite and Casting Flow

1. Admin creates a run, configures its houses/paths/years/clubs/subjects/custom attributes
2. Organizer creates invites with pre-filled casting (house, year, path, role, custom attributes). Bulk creation via CSV upload (organizers use Google Sheets).
3. Player receives an anonymous invite code, signs up or logs in, enters the code
4. Player is linked to the run with casting pre-populated. Players cannot change their own house/year/path — only organizers can.

### Posts

All posts are scoped to a run. Two types:

**Character Introduction** — the core post type:
- **Structured (filterable):** character name (includes pronouns), house, blood status, clubs, role (student/professor/staff/headmaster). Conditionally: year + path + custom attrs for students; teaching subject(s) + monitor_of_house + monitor_of_club for professors; title/position for staff.
- **Semi-structured:**
  - `keywords` — list of short descriptive strings. Autocomplete from a global shared pool, but players can type custom ones. (e.g. "Nerdy, Absentminded, Brilliant, Bookworm")
  - `looking_for` — list of { label, description }. Labels autocomplete from a global shared pool, but can be fully custom. (e.g. label: "Friends", description: "Want to be friends? Nadia is quite easy going..."; or label: "Red Ravens", description: "Are you part of Kiara's gang?")
  - `rumors` — optional list of text entries
- **Free-form:**
  - `description` — rich text. Players use this for character bio, OOC notes, plot hooks, or anything else. Intentionally unstructured.
  - `photos` — gallery (mostly portraits, occasionally mood boards)

**Other** — for extracurricular announcements, school-wide plots, club recruitment, etc:
- Title + description (rich text) + photos
- Category (extracurricular, school-wide plot, club recruitment, etc.)

### Comments

Threaded comments (Reddit-style) on posts. Used to express interest in relationships, ask questions, coordinate.

### Global Pools

Keyword and looking_for label suggestions are global (not per-run). They accumulate over time and serve as autocomplete suggestions — never a constraint.

## UI Structure

The app has two main sections per run, serving different browsing modes:

### Message Board (run home page)

All posts (student, faculty, other) in a single **chronological feed, latest first**. This is the Facebook-group-replacement experience — browse, catch up on new posts, serendipitous discovery. No filters. Posts display as **previews** (name + first few lines) that can be expanded in place.

### "Let me discover..." section

Directed search and structured browsing. Three sub-sections:

**Faculty** — all professors/staff/headmaster displayed as **cards** (portrait, name, teaching subject, house monitored). Small group (~12 professors), shown all at once. Click a card to see the full post. Professors have a privileged display because every student interacts with them through classes.

**Students** — filterable list:
- Hard filters: house, year, path, clubs, blood status, custom attributes
- Keyword filter: clicking a keyword filters on it. Exact matches shown first; semantically related keywords (e.g. "intellectual" → "analytical", "bookworm", "nerd") shown below with less priority. Semantic expansion is a v2 feature (embedding-based); MVP uses exact match only.
- Free text search across name, description, looking_for
- **"Someone you might meet in the hallways"** widget: surfaces 1-3 random posts outside current filters. Refreshes on page load. Preserves serendipity within the directed search experience.

**Other posts** — announcements, school-wide plots, club recruitment. Filterable by category.
