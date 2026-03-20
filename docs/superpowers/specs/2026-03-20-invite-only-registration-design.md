# Invite-Only Registration Flow

## Context

The app currently allows open registration at `/accounts/signup/`. Players sign up freely, then separately claim invite codes at `/accounts/claim/<uuid>/`. This exposes registration to the open internet and splits the onboarding into two disconnected steps.

The goal is to make the invite link the single entry point for new players. No open registration — you need a link to create an account.

## Design

### URL Changes

| Before | After |
|--------|-------|
| `/accounts/signup/` | **Removed** |
| `/accounts/claim/<uuid>/` | **Removed** |
| — | `/<run-slug>/join/<uuid>/` (new) |
| `/accounts/login/` | Kept as-is |
| `/accounts/social/` | Kept as-is |

The join URL lives at the top level with the run slug prefix for context. Reads naturally: `/czocha-23/join/a1b2c3d4.../`.

The new route goes **after** all prefix-based includes in `config/urls.py` to avoid the bare `<slug>/` pattern shadowing `/admin/`, `/accounts/`, etc.

### The Join Page

**Unauthenticated visitor sees:**
- Top: casting details (run name, character name, role, house, year, path — whatever the organizer pre-filled). Read-only.
- Bottom: email/password signup form, social login buttons (with `?next=/<run-slug>/join/<uuid>/`), and "Already have an account? Log in" link (also preserving `next`).

**Authenticated visitor sees:**
- Same casting details at top.
- "Join as [character name]" confirmation button.
- Validation errors if invite is already claimed or user already has a casting in this run.

### Join View Logic

```
GET /<run-slug>/join/<uuid>/
├── Validate: invite exists, run slug matches invite's run → 404 if not
├── Validate: run is active → 404 or friendly message if not
├── Validate: invite not already claimed → error message
├── If authenticated:
│   ├── Validate: user doesn't already have a casting in this run → error
│   └── Render: casting details + confirm button
└── If unauthenticated:
    └── Render: casting details + signup form + social buttons + login link

POST /<run-slug>/join/<uuid>/
├── If unauthenticated + signup form submitted:
│   ├── Create user (role=player)
│   ├── Log them in (with explicit backend kwarg)
│   └── Redirect to same URL (now authenticated, they'll see confirm step)
└── If authenticated + confirm submitted:
    ├── Link casting to user
    ├── Mark invite as claimed
    ├── Handle IntegrityError from unique_user_per_run → friendly "already in run" error
    └── Redirect to message board for the run
```

Two-step for new users (signup then confirm), one-step for existing users (confirm only). Social login is always two-step because of the OAuth redirect, but the `next` param brings them back.

### Landing Page & Login Changes

**Landing page (`/`):**
- Remove "Sign up" button and social login buttons.
- Keep only "Log in" button.
- Adjusted copy to mention invite links.

**Login page (`/accounts/login/`):**
- Stays as-is (email/password + social login buttons).
- Remove "Don't have an account? Sign up" link.

### What Gets Removed

**Views:**
- `PlayerSignupView` in `accounts/views.py`
- `ClaimInviteView` in `accounts/views.py`

**Forms:**
- `SignupForm` in `accounts/forms.py` — renamed to `JoinSignupForm` and kept for use in the join view. Same fields (email, password, password_confirm), same logic.

**URLs:**
- `accounts/signup/` route in `accounts/urls.py`
- `accounts/claim/<uuid>/` route in `accounts/urls.py`

**Templates:**
- `templates/player/signup.html`
- `templates/player/claim_invite.html`

**Tests to remove/rewrite:**
- `test_signup_page_has_social_buttons` — references removed `accounts:signup` URL
- `test_signup_social_buttons_preserve_next` — same
- `test_signup_redirect` — tests `get_signup_redirect_url` which is now just a fallback

### Blocking Allauth's Built-in Signup

Allauth registers its own signup view at `/accounts/social/account/signup/`. Without intervention, this remains an open registration backdoor. Fix: add `is_open_for_signup()` returning `False` to `LFRAccountAdapter`. This tells allauth that standalone signup is not allowed — it will only create accounts through social login flows (which are gated by OAuth providers).

```python
class LFRAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
    ...
```

### Social Login

`LFRSocialAccountAdapter.save_user()` continues to set `role=player`. Social signup from the join page works via `next` parameter: player clicks Google → OAuth → account created → redirected back to join page → they see confirm step → done.

`LFRAccountAdapter.get_signup_redirect_url()` becomes unused since standalone signup is gone, but is kept as a harmless fallback with a comment explaining this.

`templates/socialaccount/signup.html` (the fallback when a provider returns no email) stays functional — allauth handles the `next` parameter through this intermediate step automatically.

### Dashboard Invite Templates

The organizer-facing invite templates currently copy raw UUIDs. They need updating to copy full URLs:

- `templates/dashboard/invites/list.html` — copy button should produce `/<run-slug>/join/<uuid>/`
- `templates/dashboard/invites/_generated.html` — same

This is essential — organizers need to send players usable links, not raw codes.

### Tests

**New tests:**
- Join page shows casting details when unauthenticated
- Join page shows signup form when unauthenticated
- Join page shows social login buttons when unauthenticated
- Join page shows confirm button when authenticated
- Signup via join page creates player account (role=player)
- Signup via join page redirects back to join (now authenticated)
- Confirm claims the invite and links casting to user
- Confirm redirects to message board
- Already claimed invite shows error
- User already in run shows error
- Run slug mismatch returns 404
- Inactive run returns error
- Concurrent confirm handled gracefully (IntegrityError)
- Social buttons preserve next param
- `/accounts/signup/` returns 404
- Allauth's `/accounts/social/account/signup/` is blocked
- Landing page has no signup button
- Login page has no signup link

**Existing tests to remove:**
- `SocialLoginButtonTests.test_signup_page_has_social_buttons`
- `SocialLoginNextParameterTests.test_signup_social_buttons_preserve_next`
- `AccountAdapterRedirectTests.test_signup_redirect`

### Key Decisions

- **High-trust environment** — casting details are shown to unauthenticated visitors on the join page. A wrong link would be quickly reported.
- **Explicit confirmation required** — even logged-in users must confirm before claiming, to handle shared devices.
- **Two-step for new users** — signup then confirm, rather than atomic, because social OAuth inherently requires two steps and the UX should be consistent.

### Known Limitations

- **Run slug changes break outstanding invite links.** If an admin changes a run's slug after links are distributed, all existing links 404. This is acceptable for now — slug changes are rare and organizers can re-send links.
