# Inclusive Reading Assistant

An AI-powered reading assistant designed to make educational content easier to understand while preserving the user's control over the original text.

## Project Overview

The system provides three AI-powered reading operations using FastAPI and Google's Gemini API:

- **Simplify:** Rewrites text in easier language while preserving its original meaning.
- **Summarize:** Creates a shorter version of the provided text.
- **Explain:** Explains a specific term or concept using the provided text as context.

The backend is stateless and does not permanently store or modify the user's original text.

## Technologies

- Python
- FastAPI
- Pydantic
- Google Gemini API
- Uvicorn
- Pytest

## Project Structure

```text
Inclusive_Reading_Backend/
├── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements-dev.txt
└── tests/
    ├── test_http.py
    └── test_logic.py
```

## Setup and Installation

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install fastapi "uvicorn[standard]" pydantic python-dotenv google-genai
pip install pytest httpx
```

### 3. Configure environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Never commit your real API key to GitHub.

### 4. Run the backend

```bash
uvicorn main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

All endpoints use POST requests and require explicit user action through `user_action: true`.

### 1. Simplify

`POST /simplify`

Example request:

```json
{
  "text": "Artificial intelligence is changing education.",
  "user_action": true,
  "level": "simpler"
}
```

Response includes:

- `original_text`
- `simplified_text`
- `level`

Available levels: `base`, `simpler`, `closer`.

### 2. Summarize

`POST /summarize`

Example request:

```json
{
  "text": "Artificial intelligence is changing education.",
  "user_action": true,
  "length": 2
}
```

Response includes:

- `original_text`
- `summary`
- `length`

Available length values: 1, 2, and 3.

### 3. Explain

`POST /explain`

Example request:

```json
{
  "text": "Artificial intelligence is changing education.",
  "user_action": true,
  "term": "Artificial intelligence",
  "style": "default"
}
```

Response includes:

- `original_text`
- `explanation`
- `style`
- `term` when provided

Available styles: `default`, `example`, `technical`.

## User Control and Source Grounding

- AI operations require an explicit user action.
- The original text is preserved and returned in every successful response.
- Simplifications and explanations are grounded in the supplied text.
- The system is designed to preserve important information, including numbers, dates, and negations.
- The backend does not automatically process text without a user request.

## Error Handling

The API handles common errors, including:

- Missing API configuration.
- Invalid requests.
- Empty AI responses.
- Gemini API failures.
- Request timeouts.

HTTP error responses use appropriate status codes and readable error details.

## Running Tests

Run the automated test suite:

```bash
python -m pytest -v
```

## Frontend Integration

The frontend communicates with the FastAPI backend through HTTP POST requests.

Default backend address:

`http://127.0.0.1:8000`

Make sure the backend is running before opening the frontend.

## Security Notes

- Keep `.env` private.
- Never expose API keys in frontend JavaScript.
- Do not commit credentials to GitHub.
