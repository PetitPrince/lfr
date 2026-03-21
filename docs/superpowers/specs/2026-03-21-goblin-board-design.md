# Goblin Board — Staff Coordination App for LARP Events

A real-time scheduling board and staff coordination tool for live action roleplay events. Designed to replace the magnetic whiteboard used in the Goblin Office (staff room) at Czocha Castle.

## Goals

1. **Primary:** Give coordinators a live overview of where staff, scenes, and equipment are at any moment during the event.
2. **Secondary:** Give field staff a personal, glanceable view of their assignments with arrival confirmation.
3. **Learning:** Explore WebSocket-based real-time communication in a practical context.

## Non-Goals

- This is not a player-facing app. Only staff use it.
- This does not replace the LFR pre-game app. It operates during the event.
- No live API integration with external systems — all imports are batch, file-based.

## Context

The "Witchards" association organizes LARP weekends at Czocha Castle. During events, ~15 staff ("goblins") coordinate scenes (NPC appearances, prop setups, scenography) across ~31 castle locations. Coordination currently happens via a magnetic whiteboard and verbal dispatch from the staff room (Goblin Office).

Players submit scene requests via Google Forms before and during the event. A coordinator reviews requests, assigns staff and equipment, and dispatches people. Staff return to the Goblin Office between assignments for further dispatch.

### Terminology

- **Goblin** — staff member, in-game persona for crew
- **Spirit of the castle** — a staff member moving unseen (wearing a brown cloak, ignored by players)
- **Scene** — any event requiring staff: NPC appearances, prop setups, teaching classes, scenography
- **Supporting Cast** — staff who play NPCs
- **Scene request** — a player-submitted form requesting staff participation

## Relationship to the LFR App

This is a **separate standalone project** with its own repository and deployment. It connects to the LFR ecosystem only through a **read-only data bridge**: CSV/JSON import of player and character data so that scenes can reference players without re-entry.

The LFR app handles the pre-game phase. This app handles the during-game phase. No shared database, no live API calls between them.

## Tech Stack

- **Backend:** FastAPI (Python) — REST API + WebSocket endpoint
- **Database:** SQLite — sufficient for ~15 concurrent users, single-server deployment
- **ORM:** SQLAlchemy (async)
- **Templates:** Jinja2 — server-rendered HTML pages
- **Frontend:** Alpine.js for reactivity + vanilla JS WebSocket client
- **CSS:** Plain CSS with CSS Grid for board layout, no framework
- **Auth:** Session-based (cookie), username/password
- **Server:** Uvicorn (ASGI)
- **Package manager:** uv
- **Testing:** pytest
- **No external services:** no Redis, no Postgres, no message broker

## Data Model

### Event

A single LARP run (e.g. "College of Wizardry 23").

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| name | str | e.g. "College of Wizardry 23" |
| start_date | date | |
| end_date | date | |
| board_token | str | Auto-generated. Used to authenticate the big screen view's WebSocket connection. |

### TimeSlot

Named time blocks within an event's timetable.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| name | str | e.g. "Period 1", "Lunch", "Free time" |
| start_time | datetime | |
| end_time | datetime | |
| sort_order | int | Display ordering |

### Location

A place in the castle. Each event defines its own set of locations. Locations can be copied from a previous event for convenience (UX feature, not a model concern).

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| name | str | e.g. "Marble Hall" |
| area_group | str | Cellar, Ground Floor, Level 1, Level 2, Outdoors |
| sort_order | int | Within its area group |

Example locations for Czocha: Alchemy Cellar, Goblin Office, Ancient Runes, Vault, Marble Hall, Grand Library, Knight's Hall, Main Hall, The Lost Chambers, Inner Courtyard, Astronomy Tower, Tavern, Path to the Dungeon, Outer Courtyard, The Forest, Gazebo, Fireball Pitch, Front of the Castle, Lower Bridge Quarters, Outer Garden, Gathering Room, Announcement Balcony, Level 1 Corridor, Faust Common Room, Libussa Common Room, Teacher's Lounge, Level 2 Common Room, Durentius Common Room, Molin Common Room, Sendivogius Common Room, Hallway next to Alchemy Cellar.

### Staff Member

A crew person who uses the app.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| name | str | |
| role | str | Free-form string. Examples: "coordinator", "supporting_cast", "scenographer", "technician". Access control: `role = "coordinator"` grants full access, all other values get field staff access. |
| username | str | Unique, for login |
| password_hash | str | Hashed password |

### Player (imported)

Imported from external data (CSV/JSON from the LFR app or organizer spreadsheets). Used for reference when building scenes — not an app user.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| player_name | str | Off-game name |
| character_name | str | |
| character_photo | str | URL or file path, nullable |
| costume_photo | str | URL or file path, nullable |
| house | str | Nullable — for reference |
| year | str | Nullable — for reference |
| player_role | str | student, faculty, staff, headmaster |
| import_source_id | str | Nullable — for matching during re-import |

### Equipment

A trackable physical item.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| name | str | e.g. "Smoke Machine", "Wireless Speaker #1" |
| current_location_id | int | FK → Location, nullable (null = in Goblin Office / storage) |
| is_operational | bool | Default true. False = broken, cannot be assigned. |
| notes | str | Nullable. Context for status, e.g. "nozzle jammed" |

**Equipment location tracking:** `current_location_id` represents where the equipment physically is right now, independent of scene assignments. When a coordinator marks a scene as `active`, `current_location_id` is automatically updated to the scene's location. When a scene is `completed`, `current_location_id` remains at the last known location (equipment stays where it was used until someone moves it). The coordinator can also move equipment manually at any time. The board displays `current_location_id` as the source of truth for "where is it now", and scene assignments as "where does it need to be."

### Scene

The core scheduling unit. Represents any activity requiring staff participation.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| title | str | |
| description | text | Full scene description |
| npc_description | text | Nullable — description of NPC(s) needed |
| scenography_notes | text | Nullable — what scenography is needed |
| requested_equipment | text | Nullable — free-text from the original scene request form |
| status | str | pending → confirmed → active → completed / cancelled (see Scene Status Lifecycle below) |
| location_id | int | FK → Location, nullable (null = location TBD) |
| time_slot_id | int | FK → TimeSlot, nullable |
| start_time | datetime | Nullable — for free-form scheduling (used when no time slot) |
| estimated_duration | int | Nullable — minutes |
| source | str | "manual" or "imported" |
| import_reference | str | Nullable — original CSV row reference |

**Scene scheduling rules:**

- A scene uses **either** `time_slot_id` (placed in a named slot) **or** `start_time` + `estimated_duration` (free-form), never both. If `time_slot_id` is set, time boundaries come from the TimeSlot. If `start_time` is set, the end is `start_time + estimated_duration`.
- Both can be null — the scene is "unscheduled" and appears in a separate "Unscheduled" section on the board. It has no time boundaries and is excluded from overlap detection.
- `estimated_duration` can be null for free-form scenes — in that case the scene is treated as a point-in-time event (no end, no overlap detection).
- **Overlap detection** always compares concrete time ranges: `[TimeSlot.start_time, TimeSlot.end_time]` or `[Scene.start_time, Scene.start_time + estimated_duration]`. Unscheduled scenes and scenes without a computable end time are excluded from overlap checks.

**Many-to-many relationships:**

- `scene_staff` — Scene ↔ Staff Member (assigned staff, typically 2–3 per scene but no hard limit enforced by the system)
- `scene_players` — Scene ↔ Player (involved players, with `is_requestor` boolean flag)
- `scene_equipment` — Scene ↔ Equipment (assigned/tracked equipment)

### Arrival Confirmation

The "I'm here" signal from a staff member.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| staff_id | int | FK → Staff Member |
| scene_id | int | FK → Scene |
| timestamp | datetime | When the confirmation was sent |

Existence of a record = confirmed. No record = not yet confirmed. Unique constraint on `(staff_id, scene_id)` — a staff member confirms arrival at a scene once.

### Scene Status Lifecycle

All transitions are **manual coordinator actions**:

- `pending` — scene is entered but not yet reviewed/approved
- `confirmed` — coordinator has reviewed, assigned staff/equipment, scene is ready to go
- `active` — scene is currently happening (coordinator marks it active when it starts)
- `completed` — scene is done
- `cancelled` — scene was called off

Allowed transitions: `pending → confirmed → active → completed`, `pending → cancelled`, `confirmed → cancelled`. No backward transitions — if a cancelled scene needs to be revived, create a new one.

Arrival confirmations are independent of scene status — a staff member can confirm arrival at a `confirmed` scene (they arrived early and are set up) or an `active` scene. The board shows arrival status alongside scene status, but they don't affect each other.

### Staff Availability

A staff member is **available** if they have no scene assignment where the scene status is `confirmed` or `active` and the scene's time range overlaps with the current or next time period. Time range is determined the same way as overlap detection: from the TimeSlot if the scene has one, from `start_time + estimated_duration` for free-form scenes, or excluded if unscheduled/no computable end time. "Available" is computed, not stored. The Big Screen and Coordinator views show available staff in the status bar. The coordinator sees available staff highlighted when assigning someone to a new scene.

### Pager Message

One-way message from coordinator to staff.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| event_id | int | FK → Event |
| sender_id | int | FK → Staff Member (must be coordinator) |
| text | str | Short message content |
| target_type | str | "individual", "role", or "everyone" |
| target_staff_id | int | FK → Staff Member, nullable — set when target_type = "individual" |
| target_role | str | Nullable — role value when target_type = "role", null otherwise. Matched via string equality against staff `role` field. Broadcasts to all staff whose role matches. |
| created_at | datetime | |

### Pager Receipt

Tracks delivery and read status per recipient.

| Field | Type | Notes |
|-------|------|-------|
| id | int | PK |
| message_id | int | FK → PagerMessage |
| recipient_id | int | FK → Staff Member |
| read_at | datetime | Nullable — null = unread, timestamp = read |

## WebSocket Architecture

### Connection Model

Single WebSocket endpoint per event:

```
ws://{host}/ws/event/{event_id}
```

On connection, the client sends an auth message with its session token (or board token for big screen views). The server validates the token, verifies the user belongs to the requested event (staff members can only connect to their own event), and groups the connection:

- `board` — coordinator views and big screen displays (receive all updates)
- `staff:{id}` — individual staff member (receives only personal updates + pager messages)

### Connection Manager

An in-memory Python class that tracks active WebSocket connections in a dictionary:

```
{
  "board": [ws_conn_1, ws_conn_2, ...],
  "staff:3": [ws_conn_3],
  "staff:7": [ws_conn_4],
  ...
}
```

No Redis or external broker. At ~15 concurrent connections, in-memory is sufficient.

### Message Format

All messages are JSON with a `type` and `payload`:

**Server → Client:**
```json
{
  "type": "scene.updated",
  "payload": { "id": 12, "title": "...", "status": "active" }
}
```

**Client → Server:**
```json
{ "type": "auth", "token": "session-token" }
{ "type": "arrival.confirm", "scene_id": 12 }
{ "type": "pager.read", "message_id": 5 }
```

### Broadcast Rules

| Event | Sent to | Payload |
|-------|---------|---------|
| Scene created/updated/deleted | `board` | Full scene data |
| Staff assigned to scene | `board` + `staff:{id}` | Assignment details |
| "I'm here" confirmation | `board` | Staff ID + scene + timestamp |
| Equipment assigned/moved | `board` | Equipment ID + new location |
| Scene status change | `board` + affected `staff:{ids}` | Scene ID + new status |
| Pager to individual | `board` + `staff:{id}` | Message content |
| Pager to role group | `board` + each `staff:{id}` matching role | Message content |
| Pager to everyone | `board` + all `staff:*` | Message content |
| Pager read receipt | `board` | Message ID + staff ID + timestamp |

### Data Flow

1. Coordinator performs action via REST API (create scene, assign staff, etc.)
2. FastAPI endpoint validates, updates database
3. Endpoint calls `ConnectionManager.broadcast(group, message)`
4. All connected clients in the group receive the message
5. Alpine.js reactively updates the UI

### Reconnection Strategy

- Client auto-reconnects with exponential backoff: 1s, 2s, 4s, 8s... capped at 30s
- On reconnect, client fetches full current state via REST API (no message replay)
- Server is stateless regarding message history
- Visual connection indicator on all views: "Connected" / "Reconnecting..."

## Views

### 1. Big Screen (TV / Projector) — Read-only

Replaces the magnetic whiteboard in the Goblin Office. Designed for always-on display, no interaction needed.

**Layout:**
- **Top bar:** Current time slot (highlighted) and next time slot
- **Main area:** Locations grouped by area (Cellar, Ground Floor, Level 1, Level 2, Outdoors), each showing active/upcoming scene, assigned staff with arrival confirmation status, and assigned equipment
- **Bottom bar:** Staff status summary (who's where, who's available) and equipment status (what's where, what's broken)

Only locations with active or upcoming scenes are shown prominently. Empty locations are collapsed or dimmed.

**Multi-day events:** The board shows the current day by default, determined by the server clock. A day selector allows switching between event days. The "current time slot" indicator only appears when viewing the current day.

### 2. Coordinator (Laptop / Tablet) — Full Control

Same overview layout as the big screen, plus interactive controls:

- **Create scene** — form with all scene fields
- **Import scenes (CSV)** — upload, column mapping, preview, commit
- **Edit scene** — click any scene to edit details, assign/reassign staff and equipment
- **Manage staff** — create/edit staff accounts
- **Manage equipment** — add/edit equipment, mark operational status
- **Pager** — send message to individual, role group, or everyone; view sent messages with read/unread receipts per recipient
- **Equipment conflict warnings** — displayed when assigning equipment already assigned to an overlapping scene (soft warning, coordinator can override)
- **Staff overlap warnings** — displayed when assigning staff to overlapping scenes (soft warning)

### 3. Field Staff (Phone) — Personal Board

Minimal, glanceable. Optimized for mobile.

- **Current assignment** (prominent): scene title, location, NPC description, "I'm here" button
- **Next assignment** (preview): scene title, location, time
- **Pager notifications**: message text with "mark as read" button
- **No access to full board or editing** — just personal assignments and pager

### Future: Map View

Structured board is the MVP. A map overlay (staff positions on a castle floor plan) can be added later if a suitable base image is available. The data model already supports it — locations have area groups, and staff have assigned locations.

## Data Import

### Scene Import (CSV/Excel)

For importing scene requests from Google Forms exports.

1. Coordinator uploads CSV file
2. Column mapping screen: detected columns mapped to scene fields (title, description, NPC description, location, time, player name, character name, requested equipment, etc.)
3. Preview step: shows parsed scenes, flags issues (unknown location, unrecognized player name)
4. Player matching: imported player/character names are fuzzy-matched against the Player table. Unmatched entries are flagged for manual resolution.
5. Coordinator reviews and commits the import

### Player Import (CSV/JSON)

For importing the player/character roster from LFR or organizer spreadsheets.

1. Upload CSV or JSON file
2. Map columns to player fields (player name, character name, house, year, role, photo URLs)
3. Preview and commit
4. Photos can be URLs (referenced) or uploaded files
5. **Re-import:** if a player with the same `import_source_id` already exists, the existing record is updated (not duplicated). Players already linked to scenes retain their links.

### Location Copying

When creating a new event, the coordinator can copy all locations from a previous event and then add/remove locations as needed. Avoids re-entering 31 locations for each Czocha run.

## Error Handling & Edge Cases

### Network Reliability

Castle WiFi is unreliable. The reconnection strategy (exponential backoff + full state refresh on reconnect) handles this. A visible "Reconnecting..." indicator ensures staff know when their board is stale.

### Equipment Conflicts

When assigning equipment to a scene, the system checks for time overlaps with other scenes using the same equipment. Conflicts produce a visible warning but are not a hard block — the coordinator may know the equipment will be free in time.

Broken equipment (`is_operational = false`) cannot be assigned (hard block).

### Staff Scheduling Conflicts

Warning if a staff member is assigned to scenes with overlapping times. Not a hard block — the coordinator may know one scene finishes early.

### Concurrent Edits

Last write wins. At 1–2 coordinators, this is a non-issue. WebSocket broadcasts mean both screens update immediately after either save.

## Authentication & Access Control

- **Session-based auth** with cookies. Staff log in once at the start of the event; the session persists on their device for the weekend.
- **Two access levels**, derived from the staff member's `role` field:
  - **Coordinator** (`role = "coordinator"`): full access to all views and actions
  - **Field staff** (any other role): personal board only (assignments, "I'm here", pager)
- **Big screen view** uses a dedicated URL with an event-specific token: `/board/{event_id}?token={board_token}`. The token is generated when the event is created and shown to the coordinator. No login form, no session — the token is passed as a query parameter and used to authenticate the WebSocket connection (sent in the auth message instead of a session token). This keeps the big screen simple (just open a URL) while preventing unauthorized access.
