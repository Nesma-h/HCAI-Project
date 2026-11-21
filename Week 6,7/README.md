# Inclusive Reading Assistant — Milestone 3 integrated prototype

**HAI principle:** User Control and Agency. The model must never run merely because a user pastes text or changes a preference. Each AI operation requires a separate, explicit user action. The original source is returned verbatim by the API and stays available in the interface.


## Structure

```text
backend/
  main.py                     FastAPI routes, model prompts, Gemini integration
  requirements.txt            Runtime dependencies
  requirements-dev.txt        Includes pytest + httpx
  .env.example                Configuration template (no real key)
  pytest.ini
  scripts/live_smoke.py       Runs live, synthetic API checks (uses 3 Gemini calls)
  tests/test_http.py          HTTP/OpenAPI tests with mocked model
  tests/test_logic.py         Validation, prompts, failure-path tests
frontend/
  index.html                  Semantic page structure and UI components
  styles.css                  Responsive visual design / themes / accessibility
  app.js                      Onboarding, source handling, explicit user actions, API wiring
  UI_ACCESSIBILITY_TEST_PLAN.md
  tests/ui_smoke.py           Optional browser test with mocked Gemini API
GIOVANNI_HANDOFF.md           Integration scope, tests and checklist
NESMA_HANDOFF.md              Visual/UX/accessibility work for Nesma
.gitignore                    Secrets, environments and caches excluded
```

## Windows / VS Code setup

Open a *new terminal* in the **project root**.

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

If PowerShell blocks activation, use `Set-ExecutionPolicy -Scope Process RemoteSigned` and retry. In `backend/.env`, set `GEMINI_API_KEY=...` using a **new valid key**; never upload this file. Do not share screenshots showing it. If an old key was included in a prior ZIP, revoke/rotate it.

Run the backend from the `backend` directory:

```powershell
python -m uvicorn main:app --reload
```

Go to `http://127.0.0.1:8000/docs` for the API docs. In a *second terminal* from the project root, launch the redesigned frontend:

```powershell
cd frontend
py -m http.server 5500
```

Open `http://127.0.0.1:5500` (do **not** open the HTML with a `file://` URL). The frontend talks to `http://127.0.0.1:8000`.

## Test locally

From the `backend` directory:

```powershell
python -m pytest -q
```

These tests use a mocked model (offline). They check HTTP status handling, request schemas, user control (including no model call when `user_action` is false), error messages, and OpenAPI contracts. Tests alone do **not** prove that a live Gemini call or the real browser works.

With a configured running backend, the following will send **three live Gemini requests** using **synthetic** text, then exercise negative-input paths:

```powershell
python scripts/live_smoke.py
```

A successful result verifies 200 + required JSON fields on Simplify, Summarize and Explain, 400 for blocked operations, and preservation of original text. Check semantic quality manually as well.

## Routes and contract

| Method | Path | JSON | Response keys |
|---|---|---|---|
| POST | `/simplify` | `text`, `user_action: true`, `level: base/simpler/closer` | `original_text`, `simplified_text`, `level` |
| POST | `/summarize` | `text`, `user_action: true`, `length: 1/2/3` | `original_text`, `summary`, `length` |
| POST | `/explain` | `text`, `user_action: true`, optional `term` in text, `style: default/example/technical` | `original_text`, `explanation`, `style`, optional `term` |

Errors: HTTP `400` blocked/invalid user action or term; `422` schema error; `502` upstream failure/empty output; `503` missing configuration; `504` timeout. Swagger now documents each of these statuses.

The interface also provides `Retry`, `Restore original`, `Undo` and a fallback pointing to a human/official academic source. **Fallback is not live human messaging** and should never be presented as such.

## Implementation vs future work

- **Functional integration improvements retained in this handoff:** checkbox preferences no longer auto-trigger AI; explicit action chips trigger the request; retry replays the actual failed request; original stays available; after repeated request failures the user is offered a manual academic support option; unsupported upload file formats are no longer advertised in the picker. The redesign is now implemented as separate HTML/CSS/JS files.
- **Known limitations:** Gemini may return an inaccurate paraphrase; quality and grounding metrics are Mina's work. The backend `user_action` boolean is a contract, **not proof of a physical click** unless confirmed in UI testing. Timeout stops awaiting but cannot guarantee cancellation of a model call already running. Text length max 12,000 characters; PDF/DOCX/image extraction is **not implemented**. Suggested clickable term highlights include predefined phrases, but the source panel also supports selecting or typing any exact phrase from the original for explanation.
- **Onboarding and responsive design:** implemented in the redesigned frontend; final manual accessibility audits (NVDA, 200% zoom, keyboard checks) still need team acceptance.
- **Deployment:** This is a local demonstration, not a production security-hardened service. It does not include auth, quota controls or rate limiting.

## GitHub requirements

- Never commit `backend/.env`, `.venv/`, keys or chat recordings containing personal information.
- Confirm first: `git status --short` and `git diff --cached --name-only`.
- The repo must contain runnable backend code and this README, and each member must commit from their own account within the submission period.
- The ZIP here is just a transfer of source; **submission is the team's existing GitHub repository**, not a ZIP or slide image.

## Nesma frontend redesign (Weeks 6–7)

The split frontend (`frontend/index.html`, `frontend/styles.css`, `frontend/app.js`) includes a **three-stage onboarding** (static demonstration → guided opt-in practice → independent use), persistent original-text panel on desktop / openable on mobile, a label-driven field to explain any exact phrase in the source, explicit consent without auto-running Gemini, visible focus, status text, readable spacing, mobile layout, and accessibility controls. No API endpoint contract was changed.

For step-by-step UI verification see `frontend/UI_ACCESSIBILITY_TEST_PLAN.md`; optional Playwright-based mocked UI tests are in `frontend/tests/ui_smoke.py`. The main design pack (editable Word + PDF) is stored separately in this handoff bundle, for the Drive submission. Team acceptance still needs real Gemini verification against this revised frontend, keyboard-only / screen-reader / 200% zoom testing and final QA.


### What changed in the design-only revision

- Clean white-mode reading-tools sidebar, clearer preferences, responsive reading workspace, and separate source-document pane.
- More prominent greeting and "you are in control" message; visual, keyboard-accessible three-stage tutorial.
- The prior working API endpoints, request schemas, Retry, Undo, Restore Original and no-auto-run flow were preserved. Gemini API keys remain in the local backend only.
- HTML, CSS and JavaScript are now in **three separate files**. Keep all three inside the `frontend/` folder when copying to GitHub. They rely on relative paths `./styles.css` and `./app.js`.
- Backend regression: **41 automated tests passed**. Browser mock test covers three-stage onboarding, all 3 actions, Retry, Restore Original, mobile source drawer, and no auto-run. **Live Gemini + final manual accessibility verification still needed after merging.**

### White-mode responsive fix (21 November 2026)

- The application now stays in White Mode independently of the operating-system dark-mode preference. The optional reading background selector still affects chosen output text only.
- On viewports 900px wide and below, Settings is collapsed on first load. Tapping the menu expands a capped-height section **above** the chat instead of covering it. A Close settings button returns focus to the menu.
- Verified with headless Chromium at 320, 390, 600, 768 and 900px widths: no sidebar/chat overlap or horizontal overflow. Frontend interactive flow verified using mocked Gemini replies (not a live Gemini test).
- Images in `Design_Deliverables/` are captured from the delivered HTML/CSS/JS rendered in Chromium, not separately produced concept art; guided-practice AI replies in screenshot-only scenarios are simulated.
