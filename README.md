# Inclusive Reading Assistant

An AI-powered academic reading assistant designed to help university students understand complex English academic texts through three user-controlled features: **Simplify, Summarize, and Explain**.

The project focuses on improving text accessibility while preserving the user's control over AI-generated transformations.

## 1. Project Overview

Academic materials often contain complex vocabulary, long sentences, and difficult concepts. The Inclusive Reading Assistant aims to make these materials easier to understand without removing access to the original content.

### Core Features

- **Simplify:** Rewrites complex academic text using clearer and simpler language.
- **Summarize:** Produces a concise version of the provided text while preserving its main ideas.
- **Explain:** Provides an accessible explanation of difficult academic content.

### Design Principle: User Control and Agency

The system follows a user-centered interaction principle:

- AI actions require an explicit user action.
- The original text remains available to the user.
- AI-generated content is presented as assistance, not as a replacement for the original material.

## 2. System Architecture

The current implementation includes a FastAPI backend connected to Google's Gemini model.

```text
                 User Request
                      |
                      v
              FastAPI Backend
                      |
                      v
             Request Validation
                      |
             +--------+--------+
             |        |        |
             v        v        v
          Simplify Summarize Explain
             |        |        |
             +--------+--------+
                      |
                      v
                Prompt Design
                      |
                      v
                Gemini API
                      |
                      v
             Generated Response
                      |
                      v
                API Response
```

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend development |
| FastAPI | REST API development |
| Google Gemini API | AI text generation |
| Google Gen AI SDK | Communication with Gemini |
| Pydantic | Request validation |
| Uvicorn | Local API server |
| Hugging Face Datasets | WikiLarge dataset access |
| Evaluate / SARI | Text simplification evaluation |

## 4. Backend Structure

```text
backend/
└── Inclusive_Reading_Backend/
    ├── main.py
    ├── requirements.txt
    ├── .gitignore
    └── evaluation/
        ├── load_dataset.py
        ├── prepare_sample.py
        ├── run_evaluation.py
        ├── calculate_sari.py
        └── results/
            ├── evaluation_sample.json
            ├── model_outputs.json
            └── sari_results.json
```

### Main Backend Components

- `main.py`: Defines the FastAPI application, API endpoints, request validation, and Gemini integration.
- `requirements.txt`: Contains the backend runtime dependencies.
- `evaluation/`: Contains the dataset preparation, model evaluation, and evaluation results.

## 5. Getting Started

### Prerequisites

- Python 3.10 or later
- A Google Gemini API key
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Nesma-h/HCAI-Project.git
cd HCAI-Project
```

### Step 2: Navigate to the Backend

```bash
cd backend/Inclusive_Reading_Backend
```

### Step 3: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

Create a `.env` file in the backend directory:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your own Gemini API key.

**Important:** Never upload your `.env` file or expose your API key publicly.

### Step 6: Run the Backend

```bash
uvicorn main:app --reload
```

The API will be available locally at:

`http://127.0.0.1:8000`

## 6. API Documentation and Endpoints

Interactive API documentation is available through Swagger UI:

`http://127.0.0.1:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Backend health check |
| POST | `/simplify` | Simplifies the submitted text |
| POST | `/summarize` | Summarizes the submitted text |
| POST | `/explain` | Explains the submitted text |

### Example Request

The three POST endpoints accept a text input and a user action indicator.

```json
{
  "text": "Your academic text goes here.",
  "user_action": true
}
```

### Request Validation

The backend validates incoming requests:

- Empty or whitespace-only text is rejected.
- Text exceeding the configured 12,000-character limit is rejected.
- Requests with `user_action` set to `false` are rejected.
- AI generation failures are handled through API error responses.

## 7. Model Evaluation

The text simplification feature was evaluated using the **WikiLarge Test Split** dataset.

A pilot evaluation was conducted using 30 randomly selected examples.

| Evaluation Item | Result |
|---|---|
| Dataset | WikiLarge Test Split |
| Model | Gemini 3.5 Flash Lite |
| Evaluated Examples | 30 |
| SARI Score | **34.81** |

SARI is an evaluation metric commonly used for text simplification. It measures the quality of operations such as adding, deleting, and keeping words compared with reference simplifications.

**Evaluation Note:** This is an initial pilot evaluation, not a comprehensive assessment. Since WikiLarge mainly contains general Wikipedia text, further evaluation on academic passages and manual assessment of readability and meaning preservation are needed.

Evaluation scripts and generated results are available in the `evaluation/` directory.

## 8. Implementation Status

| Component | Status |
|---|---|
| FastAPI backend | Implemented |
| Simplify endpoint | Implemented and tested |
| Summarize endpoint | Implemented and tested |
| Explain endpoint | Implemented and tested |
| Request validation | Implemented and tested |
| Gemini integration | Implemented |
| WikiLarge pilot evaluation | Completed |
| Frontend interface | Pending |
| Frontend-backend integration | Pending |

## 9. Backend Demonstration

Watch the backend demonstration video, showcasing the API endpoints and their responses:

[Watch the Backend Demo on Google Drive](https://drive.google.com/drive/folders/1PrXm_n6Lh8fk0Nygxikit38mTvwqyHli?usp=sharing)

## 10. Repository

GitHub Repository:

https://github.com/Nesma-h/HCAI-Project

---

**Inclusive Reading Assistant**  
Human-AI Interaction Project  
Faculty of Computers and Artificial Intelligence – Benha University
