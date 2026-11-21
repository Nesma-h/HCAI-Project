# Frontend design — Nesma / Weeks 6–7

## Source files
- `index.html` — page semantics, accessible labels, and component containers. Uses the same IDs used by the JavaScript app.
- `styles.css` — permanent white-mode visual system, responsive layout, high-contrast focus styles, in-flow mobile settings, mobile original-text panel and onboarding styling.
- `app.js` — unchanged core contract for `/simplify`, `/summarize`, `/explain`, user-initiated actions, recovery and version controls, with a redesigned welcome message.

**Do not upload a stand-alone `index.html`**: this revision needs the CSS and JavaScript files beside it. Never put an API key in a frontend file.

## Run
From the `frontend/` directory: `py -m http.server 5500` on Windows. Open `http://127.0.0.1:5500`. Separately run FastAPI from the `backend/` directory: `python -m uvicorn main:app --reload`. The API URL is `http://127.0.0.1:8000`.

## Verification
From project root: `python -m pytest backend/tests -q` (offline backend tests), then optionally `python frontend/tests/ui_smoke.py` (requires `pip install playwright` + `python -m playwright install chromium`). The UI test uses mock API responses; verify an actual Gemini response separately on your own system.

Test manually: first-run tour stages 1–3; click sample without any API request; then click Simplify; original source must remain; summarize; explain any existing phrase; Restore Original; Stop backend and use Retry after restart. Retest in Edge on 390px mobile width, keyboard-only, screen reader, and 200% zoom.

## Handoff note
This is the **white-mode** production-candidate frontend. On widths up to 900px the settings sidebar opens above the chat (never over it), is closed initially, and has a visible Close settings control. A new Word/PDF design pack with screenshots rendered from these actual frontend files is included in `Design_Deliverables/`. Browser images reflect real DOM/CSS/JS in Chromium; model replies in UI-only tests are simulated. Test live Gemini separately.
