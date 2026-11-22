# Inclusive Reading Assistant

**Milestone 3 --- Weeks 6--7 \| Human--AI Interaction (HCAI)**\
**HAI principle:** User Control and Agency

Inclusive Reading Assistant is a web-based tool that helps university
students work with difficult English academic text. Students can
**simplify**, **summarize**, or **explain** content using Google Gemini
through the team's own FastAPI backend.

**The student stays in control:** pasting a passage, selecting a term,
or changing a preference never triggers an AI request on its own. The
student must explicitly select an action. The original text stays
accessible, and AI-generated responses can be undone or replaced with
the original.

## Features

-   **Simplify:** rewrite a passage in clearer English while aiming to
    preserve its meaning.
-   **Summarize:** create a short, medium, or detailed summary.
-   **Explain:** explain a word or phrase from the original text in
    context.
-   **User control:** no automatic AI processing; explicit action
    buttons, **Undo**, **Restore original**, and **Retry**.
-   **Three-stage onboarding:** watch an example, try a guided task,
    then work independently with Help available.
-   **Accessible, responsive interface:** white-mode UI, reading
    preferences, keyboard-friendly controls, and mobile settings that do
    not cover the chat.
-   **Error recovery:** readable feedback for invalid input, unavailable
    services, and timeouts; guidance to academic support when assistance
    cannot be provided reliably.

AI outputs can contain mistakes. Always compare results with the
original academic source.

## Repository structure

``` text
Inclusive-Reading-Assistant/
│
├── backend/
│   │
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── scripts/
│   │   └── live_smoke.py
│   │
│   
├── evaluation/
│   ├── semantic_similarity.py
│   ├── meaning_preservation.py
│   ├── calculate_operational_metrics.py
│   ├── calculate_metrics.py
│   │
│   ├── scripts/
│   │   ├── api_client.py
│   │   ├── calculate_metrics.py
│   │   ├── evaluation_runner.py
│   │   └── prepare_dataset.py
│   │
│   ├── dataset/
│   │   ├── wikilarge_hf_test.xlsx
│   │   ├── wikilarge_test.xlsx
│   │   ├── wikilarge_test_clean.json
│   │   └── wikilarge_test.json
│   │
│   └── results/
│       ├── meaning_preservation_results.xlsx
│       ├── meaning_preservation_summary.json
│       ├── baseline_operational_metrics.json
│       ├── baseline_individual_metrics.xlsx
│       ├── baseline_metrics.json
│       ├── wikilarge_evaluation_results.xlsx
│       ├── wikilarge_evaluation_results.json
│       ├── metrics_summary.json
│       ├── evaluation_results.xlsx
│       └── evaluation_results.json
│
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── .gitignore
└── README.md
```

The `tests/` folders are **not required to start or use the
application** and may be omitted from this repository. If you do not
upload the optional `backend/scripts/` folder, the website and API will
still run normally.

## Requirements

-   Python **3.11 or newer**
-   A valid **Google Gemini API key** from [Google AI
    Studio](https://aistudio.google.com/apikey)
-   A modern web browser (Microsoft Edge or Chrome recommended)

## Setup and run on Windows (PowerShell)

### 1. Start the backend

Open the project folder in VS Code, then open a terminal in the project
root:

``` powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell blocks virtual-environment activation, run this once in
the current terminal, then activate again:

``` powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

If your GitHub copy does not contain `.env.example`, create a new file
named **`.env`** locally inside `backend/` instead of running the
`Copy-Item` command.

Open **`backend/.env`** (the private file you created) and configure:

``` env
GEMINI_API_KEY=YOUR_VALID_GEMINI_API_KEY
GEMINI_TIMEOUT_SECONDS=60
```

Replace the placeholder with your own key. **Never commit or share the
`.env` file or a real key.** The `.env.example` file must contain
placeholders only.

Start FastAPI **from the `backend/` folder**:

``` powershell
python -m uvicorn main:app --reload
```

The API documentation is available at
[**http://127.0.0.1:8000/docs**](http://127.0.0.1:8000/docs).

### 2. Start the frontend

Leave the backend terminal running. Open **a second terminal** from the
project root:

``` powershell
cd frontend
py -m http.server 5500
```

Open [**http://127.0.0.1:5500**](http://127.0.0.1:5500) in your browser.

> Run the frontend through its local web server, not by double-clicking
> `index.html`. The frontend makes requests to `http://127.0.0.1:8000`
> (configured in `frontend/app.js`). Keep both terminals open while
> using the application.

## How to use the app

1.  Open the website and follow or skip the three-stage onboarding.
2.  Click **Try sample text**, paste a passage, or upload a `.txt` /
    `.md` file.
3.  Choose **Simplify**, **Summarize**, or **Explain**. No AI request is
    sent just by loading the text.
4.  Read the AI response and compare it with the original text in the
    source panel.
5.  Use **Undo**, **Restore original**, **Retry**, or **Help** as
    needed.

For **Explain**, select a phrase from the source text or enter an exact
phrase contained in that source, then click **Explain selected phrase**.

## Backend API

  ----------------------------------------------------------------------------
  **Method**        **Endpoint**      **Purpose**       **Required request
                                                        fields**
  ----------------- ----------------- ----------------- ----------------------
  `GET`             `/`               Backend status    ---

  `POST`            `/simplify`       Simplify text     `text`,
                                                        `user_action: true`;
                                                        optional `level`
                                                        (`base`, `simpler`,
                                                        `closer`)

  `POST`            `/summarize`      Summarize text    `text`,
                                                        `user_action: true`;
                                                        optional `length`
                                                        (`1`, `2`, `3`)

  `POST`            `/explain`        Explain text or a `text`,
                                      term              `user_action: true`;
                                                        optional `term` and
                                                        `style` (`default`,
                                                        `example`,
                                                        `technical`)
  ----------------------------------------------------------------------------

Example request for **`POST /simplify`**:

``` json
{
  "text": "The intervention reduced reading time but did not improve comprehension.",
  "user_action": true,
  "level": "base"
}
```

A successful Simplify response includes `original_text`,
`simplified_text`, and `level`. The other endpoints return
`original_text` with `summary` / `explanation` and their selected
options.

**Error codes:** `400` for rejected actions or invalid terms, `422` for
invalid request data, `502` for upstream AI errors, `503` if the API key
is not configured, and `504` if the model request times out.

## Model Evaluation

The text simplification feature was evaluated using the **WikiLarge Test
Split** dataset. Multiple evaluation runs were conducted during
development to assess simplification quality, API reliability, and
response performance.

### Evaluation setup

  Evaluation Item          Details
  ------------------------ ------------------------------------
  Dataset                  WikiLarge Test Split
  Dataset Source           Hugging Face Datasets
  Model                    Gemini 3.5 Flash Lite
  Backend                  FastAPI
  Main Evaluation Metric   SARI
  Additional Metrics       Response Time, Flesch Reading Ease
  Evaluation Framework     Custom Python evaluation scripts

### Text simplification quality results

Multiple evaluation runs were recorded during development.

  Evaluation Run                 Evaluated Examples     SARI Score
  ---------------------------- -------------------- --------------
  Initial Pilot Evaluation                       30          34.81
  Initial Quality Evaluation                      5          45.15
  Extended Evaluation                           200   37.27 (Mean)

For the extended 200-sample evaluation:

  SARI Statistic     Result
  ---------------- --------
  Mean                37.27
  Median              35.16
  Minimum              7.96
  Maximum            100.00

SARI evaluates text simplification operations such as adding, deleting,
and keeping words compared with reference simplifications.

**Evaluation note:** These scores belong to separate evaluation runs.
They should not be interpreted as a direct improvement or decline
without controlling for sample selection and evaluation setup.

### API reliability results

An extended API evaluation was conducted using 200 test samples.

  Metric                        Result
  --------------------------- --------
  Total Samples                    200
  Successful Requests              200
  Failed Requests                    0
  Missing Generated Outputs          0
  API Success Rate                100%

All 200 requests completed successfully during this evaluation run.

### Response time performance

  Performance Metric                Result
  ----------------------- ----------------
  Average Response Time     4.7165 seconds
  Median Response Time      3.5095 seconds
  P95 Response Time         9.2804 seconds
  Minimum Response Time      2.345 seconds
  Maximum Response Time     26.983 seconds

The median response time was approximately 3.51 seconds, while 95% of
measured requests completed within approximately 9.28 seconds.

### Initial readability and quality evaluation

An initial quality evaluation was performed on 5 samples.

  Metric                           Result
  ----------------------- ---------------
  Average Response Time     3.251 seconds
  Flesch Reading Ease               54.12
  SARI                            45.1547
  BERTScore                  Not Computed

BERTScore could not be calculated because of a Windows memory allocation
error (Paging File Error 1455). Therefore, no BERTScore result is
reported.

### RAG and knowledge retrieval experiment

A separate knowledge retrieval experiment examined how retrieved
information can be used to generate grounded answers.

  Retrieval Metric                Result
  ------------------- ------------------
  Retrieved Chunks                     5
  Context Length        7,920 characters
  Retrieved Sources                    5

The retrieved knowledge was used to construct a context that was passed
to Gemini for answer generation.

This was a separate retrieval experiment. It should not be interpreted
as evidence that every Simplify, Summarize, or Explain API request uses
RAG.

### Test coverage

A structured test set containing 36 test scenarios was prepared.

  Test Category                   Number of Scenarios
  ----------------------------- ---------------------
  Simplification                                    8
  Summarization                                     5
  Explanation                                       5
  User Control and Agency                           6
  Meaning Preservation                              4
  Groundedness                                      4
  Error Handling and Recovery                       4
  **Total**                                    **36**

The test set covers the three main endpoints, explicit user actions,
preservation of meaning, grounded responses, and error handling.

**Test status note:** The 36 scenarios represent the designed test
coverage. Individual execution logs and Pass/Fail results for every
scenario were not available in the evaluation records. The 200-sample
API evaluation is reported separately and does not mean that all 36
scenarios were individually executed.

### Evaluation limitations

-   WikiLarge mainly contains general Wikipedia text, so additional
    testing on university-level academic passages is needed.
-   SARI evaluates text simplification quality but does not
    independently guarantee that the original meaning has been
    preserved.
-   BERTScore was not available in the initial evaluation because of a
    memory allocation issue.
-   LLM-as-a-Judge evaluation was postponed.
-   Quantitative aggregate results for groundedness, meaning
    preservation, and Human-AI Interaction principles have not yet been
    established.
-   Manual evaluation by students or academic reviewers is recommended
    to assess readability, correctness, and usefulness.

### Evaluation conclusion

The extended evaluation achieved a **100% API success rate across 200
samples**, with a mean SARI score of **37.27** and an average response
time of **4.7165 seconds**.

The initial pilot evaluation achieved a SARI score of **34.81 across 30
examples**.

These results provide an initial quantitative assessment of the system's
operational reliability and simplification performance. Further
evaluation using academic texts and human feedback is necessary to
assess meaning preservation, accessibility, and the overall user
experience.

Evaluation scripts and generated results are available in the
`evaluation/` directory.

## Quick manual checks

After starting both servers:

1.  Load sample text without selecting an AI action --- **nothing should
    be generated automatically**.
2.  Run Simplify and check for a real response from the backend.
3.  Run Summarize and Explain.
4.  Click **Restore original** and confirm the original is unchanged.
5.  Stop the backend, request an action, restart the backend, then click
    **Retry**.
6.  View the app at mobile width and check that opening settings **does
    not cover the chat**.

These checks help confirm the working demo. They do not replace a
separate evaluation of AI answer quality.

## Current limitations

-   English text only; **PDF, DOCX, and image reading are not
    implemented** in this demo.
-   Uploaded text files are limited to `.txt` and `.md`; text requests
    have a maximum of **12,000 characters**.
-   The assistant cannot independently verify the truth of a source or
    guarantee accurate AI output.
-   `user_action` is an API contract; actual user control also depends
    on the frontend's explicit-click behavior.
-   Human handover is **guidance to a teacher, teaching assistant, or
    academic support service**, not a live transfer to a person.
-   This is a local educational prototype, not a production deployment
    with authentication or rate limiting.

## GitHub and submission notes

-   Commit the **`backend/`**, **`frontend/`**, **`.gitignore`**, and
    **`README.md`** files at the repository root.
-   Do **not** upload `.env`, `.venv/`, cached files, or API keys.
-   Use the **existing team repository**. Each team member needs a
    commit from their own GitHub account during Weeks 6--7.
-   Submit the design pack, test set, prompt log, demo video, and demo
    script separately to the team's **Drive / Week 6-7** folder using
    the instructor's required file names.

------------------------------------------------------------------------

**Inclusive Reading Assistant**\
Human--AI Interaction Project\
Faculty of Computers and Artificial Intelligence -- Benha University
