# LLD Practice Platform

LLD Practice Platform is an MVP for learners who want to practice Low-Level Design (LLD) problems repeatedly. A learner selects a problem, writes a design, submits it, receives structured feedback, and reviews the saved attempt. The current implementation combines deterministic checks with feedback from Google Gemini.

## 1. Product Goal

LLD practice is more useful when learners can repeat the same workflow and compare their thinking over time. This project focuses on that loop: provide a small problem library, preserve each submission, return actionable feedback, and make previous attempts easy to revisit.

The goal is deliberately narrower than a production learning platform. The MVP validates the learner workflow and the evaluation boundary rather than authentication, collaboration, or large-scale operations.

## 2. Core User Flow

```text
Problem Selection
        -> Practice
        -> Submit
        -> Evaluation
        -> Feedback
        -> History
        -> Review / Retry
```

1. **Problem Selection:** The home page loads problems from `GET /problems/`.
2. **Practice:** The learner opens a problem and sees its description and requirements.
3. **Submit:** The learner writes a solution and submits it. The backend rejects an unknown problem or a whitespace-only solution.
4. **Evaluation:** The frontend creates the attempt and then requests evaluation.
5. **Feedback:** A successful evaluation returns strengths, issues, suggestions, and trade-offs.
6. **History:** The history page lists saved attempts in newest-first order.
7. **Review / Retry:** An attempt can be opened again. The backend exposes retry evaluation for submitted or failed attempts; the current frontend does not yet invoke that endpoint from its “Try Again” button.

## 3. Features

### Problem Practice

- Lists problems stored in SQLite.
- Displays a problem description and a list of requirements.
- The seed script currently provides Parking Lot, Vending Machine, and Elevator System problems.
- Provides a text area for describing classes, interfaces, relationships, responsibilities, and design decisions.

### Submission / Attempts

- Validates that the selected problem exists.
- Rejects empty or whitespace-only solutions with HTTP `400`.
- Persists the solution before evaluation starts.
- Stores the problem ID, solution, status, feedback, and creation timestamp.
- Lists attempts newest first and exposes individual attempt details.

### Evaluation

- `RuleBasedEvaluator` performs simple deterministic checks on solution length, the presence of `interface`, and the presence of `class`.
- `LLMEvaluator` sends the problem and solution to Google Gemini and requests JSON feedback.
- `EvaluationService` runs both evaluators and concatenates their results by feedback category.
- The Gemini evaluator tries three configured model names sequentially and retries each model after a short delay when a call fails.

### Feedback

Feedback is persisted and returned in four categories:

- Strengths
- Issues
- Suggestions
- Trade-offs

The LLM prompt asks for feedback about responsibility distribution, SOLID principles, coupling and cohesion, abstraction and interfaces, extensibility, design patterns, explicitly stated missing requirements, design problems, and trade-offs. The deterministic evaluator adds a small set of rule-based observations.

### History

- Shows all saved attempts and their current statuses.
- Resolves problem IDs to problem titles in the frontend.
- Opens a detail view containing the original solution and available feedback.

### Failure Handling

- An attempt is committed with status `evaluating` before the external evaluation call.
- If evaluation raises an exception, the attempt is retained and marked `evaluation_failed`; the API returns HTTP `503`.
- The backend provides `POST /attempts/{attempt_id}/retry-evaluation` for retrying attempts in `evaluation_failed` or `submitted` status.

## 4. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Python, FastAPI | HTTP API and request handling |
| API | FastAPI routers, Pydantic 2 | Problem and attempt endpoints plus response validation |
| Database | SQLite, SQLAlchemy 2 | Local persistence for problems and attempts |
| Frontend | React 19, React Router, Vite | Problem, practice, history, and attempt views |
| AI | `google-genai` and Google Gemini | LLM-based LLD feedback |
| Configuration | `python-dotenv` | Loads `GEMINI_API_KEY` from environment or `.env` |
| Testing | `pytest`, FastAPI `TestClient` | Backend endpoint tests |

The pinned backend package versions are in `backend/requirements.txt`; frontend versions and scripts are in `frontend/package.json`.

## 5. Architecture

```text
React + React Router
        |
        v
FastAPI routers (/problems, /attempts)
        |
        v
SQLAlchemy models + SQLite
        |
        +--> EvaluationService
                 |
                 +--> RuleBasedEvaluator
                 |
                 +--> LLMEvaluator --> Google Gemini API
```

The repository is a small monolith. The frontend is a separate Vite development application, while the backend owns HTTP routing, persistence, and evaluation orchestration. This is appropriate for the MVP because it is simple to run, easy to test locally, and keeps attention on the learner workflow instead of distributed-systems concerns.

Evaluation is currently synchronous from the API caller's perspective. The submission request and evaluation request are separate frontend calls, but the evaluation endpoint waits for the rule-based and Gemini evaluators to finish.

The broader product direction and research/design deliverables live in `RESEARCH.md` and `DESIGN.md`. This README references those notes rather than duplicating them.

## 6. Project Structure

```text
backend/
  app/
    api/              FastAPI routers for problems and attempts
    models/           Domain dataclasses and SQLAlchemy database models
    schemas/          Pydantic request and response models
    services/         Rule-based, LLM, and combined evaluation logic
    database.py       SQLite engine and session dependency
    main.py           FastAPI application, tables, CORS, and routes
    seed.py           Local problem seed data
  tests/              Backend endpoint tests
  requirements.txt    Backend dependencies
frontend/
  src/
    pages/            Home, practice, history, and attempt screens
    components/       Reusable problem card
    App.jsx           Routes and navigation
  package.json        Frontend dependencies and scripts
README.md             Short original project overview
DESIGN.md             Concise technical design note
RESEARCH.md           Research note on the learner problem and product direction
ai_usage.md           AI usage placeholder (currently empty)
README_AI_USAGE.md    Combined submission documentation
```

## 7 Attempt Lifecycle

The normal API lifecycle is:

```text
POST /attempts/
      |
      v
  submitted
      |
POST /attempts/{id}/evaluate
      |
  evaluating
    /     \
   v       v
evaluated  evaluation_failed
              |
              v
       retry-evaluation
```

An evaluation attempt is committed as `evaluating` before `EvaluationService` is called. This matters because an unavailable Gemini service or malformed response must not erase the learner's submission. On failure, the existing attempt is committed as `evaluation_failed` and can be retried through the backend endpoint.

There are two implementation details reviewers should be aware of:

- The persisted API failure status is `evaluation_failed`, while `AttemptStatus.FAILED` is `failed`.
- The evaluate endpoint does not restrict the starting status, so an already evaluated attempt can be evaluated again. The retry endpoint is more restrictive and accepts only `evaluation_failed` or `submitted`.

## 8 Evaluation Approach

LLD does not have one universally correct class diagram. Several designs can satisfy the same requirements, so feedback needs to explain design choices and trade-offs instead of treating one implementation as the only answer.

The implementation uses two complementary signals:

1. **Deterministic checks:** `RuleBasedEvaluator` produces predictable feedback for basic indicators such as solution detail, interfaces, and class definitions. These checks are inexpensive and do not depend on an external service, but they are text heuristics rather than a full design analysis.
2. **LLM evaluation:** `LLMEvaluator` asks Gemini to review responsibility distribution, SOLID principles, coupling/cohesion, abstractions, extensibility, patterns, explicit requirements, design problems, and trade-offs. The prompt explicitly allows multiple valid solutions and asks for concrete reasons rather than personal judgment.
3. **Combination:** `EvaluationService` concatenates the result lists from both evaluators. It does not calculate a numeric score or resolve disagreement between the two evaluators.

The current production path always constructs `LLMEvaluator`, so a missing API key or unavailable Gemini service prevents evaluation even though the rule-based result could be computed independently. The rule-based evaluator is therefore complementary feedback, not a fallback path for a failed LLM call.

## 9. API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Returns an API-running message |
| `GET` | `/health` | Returns a health status |
| `GET` | `/problems/` | Lists all problems |
| `GET` | `/problems/{problem_id}` | Gets one problem or returns `404` |
| `POST` | `/attempts/` | Validates and persists a submitted solution |
| `GET` | `/attempts/` | Lists attempts newest first |
| `GET` | `/attempts/{attempt_id}` | Gets one attempt or returns `404` |
| `POST` | `/attempts/{attempt_id}/evaluate` | Runs evaluation for an attempt |
| `POST` | `/attempts/{attempt_id}/retry-evaluation` | Retries a submitted or failed evaluation |

The backend allows CORS from `http://localhost:5173`, which matches the default Vite development origin used by the frontend.

## 10 Local Setup

### Prerequisites

- Python with `venv` and `pip` available.
- Node.js and `npm` available.
- A Google Gemini API key for evaluation.

The repository does not specify minimum Python or Node.js versions. Use versions supported by the pinned dependencies in `backend/requirements.txt` and `frontend/package.json`.

### Backend

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` with the key used by `LLMEvaluator`:

```text
GEMINI_API_KEY=your_api_key_here
```

Start the API from the `backend` directory:

```powershell
uvicorn app.main:app --reload
```

### Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend currently calls `http://localhost:8000` directly, so the backend must be running on that port. The Vite development server normally runs on `http://localhost:5173`.

### Database / Seed

The SQLite database path is `backend/lld_platform.db` when the backend is started from `backend`. Tables are created during application import. Seed the three local problems explicitly from the `backend` directory:

```powershell
python -m app.seed
```

The seed script skips seeding when any problem already exists. It is not a migration system and does not update existing rows.

## 11 Environment Variables

The only application environment variable currently read is:

```text
GEMINI_API_KEY=your_api_key_here
```

The key may be provided through the environment or `backend/.env`. `.env` is excluded by `.gitignore`; never commit a real API key or include the contents of a local `.env` file in a submission.

There is no configured `DATABASE_URL` override. The database URL is defined directly in `backend/app/database.py`.

## 12 Testing

Run the backend tests from the `backend` directory:

```powershell
pytest
```

The current suite contains five endpoint tests:

- Listing problems succeeds.
- Fetching problem `1` returns the seeded Parking Lot problem.
- Fetching a missing problem returns `404`.
- An empty solution returns `400`.
- Submitting against an invalid problem returns `404`.

The tests use the application's existing SQLite database and do not create isolated database fixtures. They do not cover successful or failed Gemini evaluation, retry evaluation, attempt listing/detail endpoints, seed idempotency, or frontend behavior. `backend/test.py` is a manual Gemini invocation, not a pytest test, and requires a live API key.

## 13 Failure Handling

Submission and evaluation are separate operations. The create-attempt endpoint commits the submitted solution first. The evaluate endpoint then changes the status to `evaluating` and commits that transition before invoking the evaluators.

If evaluation raises an exception, the route commits `evaluation_failed` and returns HTTP `503`. The response explains that the submission was saved. The retry endpoint repeats evaluation for an attempt in `evaluation_failed` or `submitted` status. This preserves learner work across external API failures, although the current frontend's “Try Again” control only reloads the page instead of calling the retry endpoint.

## 14 Data Persistence

SQLite stores problems in `problems` and submissions in `attempts`. Problem requirements and attempt feedback are serialized as JSON text. SQLAlchemy creates the tables automatically when the FastAPI application is imported.

SQLite is a reasonable local choice for this MVP because it avoids a separate database service and keeps setup small. The repository does not demonstrate production-scale concurrency, backups, migrations, or multi-user data isolation.

## 15 Security / Configuration

- Gemini credentials are read from an environment variable and should not be committed.
- `.env` is excluded by `.gitignore`.
- CORS is restricted to the local frontend origin configured in `backend/app/main.py`.

The MVP has no authentication or authorization. Attempts are therefore not associated with users, and the API should not be exposed publicly without additional controls.

## 16 Key Design Decisions / Trade-offs

### Simple monolith instead of microservices

The API, persistence, and evaluation orchestration live in one backend application, with the React app as a separate frontend process. This keeps local setup and debugging straightforward. It also means the backend is responsible for the latency and availability of the synchronous evaluation call.

### Evaluator abstraction

The `Evaluator` interface and shared `EvaluationResult` allow deterministic and LLM evaluators to be invoked through the same contract. The trade-off is that the current interface is intentionally small and does not model confidence, scoring, or evaluator disagreement.

### Deterministic plus LLM evaluation

Rule checks are repeatable but shallow; LLM feedback is broader but depends on an external service and can vary. Combining both provides more useful feedback for this prototype, but the system does not yet rank, reconcile, or validate the quality of the two result sets.

### Persist before evaluation

Committing the attempt before the external call ensures that a Gemini outage does not lose learner work. The cost is an explicit failure state and a separate retry operation.

### Structured feedback

Four lists are easier for the API and frontend to render than one unstructured paragraph. They also leave room to evolve each feedback category independently. The current implementation stores the lists as JSON and does not attach severity, evidence, or scores.

### Synchronous evaluation

Waiting for evaluation is simpler for an MVP and gives the learner a direct result. It also makes request latency dependent on Gemini and the model fallback loop. Background processing and polling could be considered later if the product needs longer-running evaluations.

## 18. Limitations

- No authentication, users, or per-user attempt ownership.
- No advanced diagram editor; solutions are submitted as text.
- No code execution or semantic parsing of class diagrams.
- Rule-based checks are simple text heuristics.
- No numeric score or calibrated evaluation rubric.
- Gemini is required for the current evaluation service path.
- Evaluation is synchronous and has no background worker or queue.
- No frontend test suite is present.
- Backend tests depend on the local database and seeded data.
- The frontend hard-codes the backend URL.
- The frontend retry control does not call the implemented retry endpoint.
- Status values are inconsistent between the domain enum and persisted API behavior.
- No production observability, migrations, backups, or multi-user isolation is implemented.

## 19. Future Improvements

### Learner experience

- Connect the frontend “Try Again” action to `retry-evaluation` and show retry progress.
- Add attempt comparison and a clearer path from feedback back to a new submission.
- Add configurable API URLs and more complete loading/error states.

### Evaluation

- Make the rule-based evaluator a true fallback when Gemini is unavailable.
- Normalize status values between the domain model, database, and API.
- Add evidence, severity, or rubric metadata to feedback without forcing a numeric score prematurely.
- Add tests using a mocked evaluator rather than requiring a live Gemini call.

### Platform / infrastructure

- Add isolated test databases and fixtures.
- Add migrations if the schema begins to evolve.
- Add authentication and user-owned attempts.
- Introduce background evaluation only when synchronous latency becomes a demonstrated product problem.

## 20. Out of Scope

Microservices, queues, Kubernetes, and distributed deployment infrastructure are not part of this MVP. They could be appropriate at a different scale, but adding them here would increase operational complexity without helping validate the core choose, submit, receive feedback, review, and retry workflow.

The separate files `DESIGN.md` and `RESEARCH.md` remain assignment deliverables. They are referenced by this README but are not duplicated here.

---

# AI Usage Report

## Overview

AI assistance was used as an engineering aid for exploring the architecture, shaping the evaluator boundary, thinking through failure handling and test cases, assisting with implementation, and organizing technical documentation. Suggestions were reviewed against the actual repository and adapted to the scope and behavior of the MVP. AI output was treated as input to engineering decisions, not as an authority or a substitute for testing.

## 1. Evaluator Abstraction

### Problem

LLD feedback needs more than one evaluation strategy. Deterministic checks are useful for stable, inexpensive observations, while an LLM can discuss design quality and trade-offs. Keeping those concerns directly inside an API route would make the route harder to test and extend.

### AI-assisted suggestion

Use an `Evaluator` abstraction with a shared `EvaluationResult`, then provide separate rule-based and LLM implementations behind that contract. Put orchestration in an `EvaluationService` rather than making the API route understand each evaluator.

### Decision

**Accepted.** The repository contains `Evaluator`, `EvaluationResult`, `RuleBasedEvaluator`, `LLMEvaluator`, and `EvaluationService`.

### Why

The abstraction keeps evaluator-specific behavior in services and gives the API one evaluation entry point. It also makes future evaluator implementations possible without changing the response shape. The interface remains intentionally small because the MVP does not yet need confidence scores or evaluator metadata.

## 2. Deterministic + LLM Evaluation

Deterministic checks alone cannot discuss nuanced responsibility boundaries, coupling, extensibility, or trade-offs. LLM-only evaluation is broader but introduces external availability, response-format, latency, and consistency risks.

The implemented hybrid approach runs both evaluators and concatenates their four feedback lists. The LLM prompt asks for structured JSON and explicitly states that multiple designs can be valid. This approach was accepted for the prototype, with the limitation that rule-based feedback is not currently used as a fallback when `LLMEvaluator` cannot be constructed or all Gemini models fail.

## 3. Persist Submission Before Evaluation

AI evaluation is an external dependency. A missing key, unavailable model, malformed response, or network failure should not destroy the learner's work.

The implementation creates and commits the attempt first with status `submitted`. The evaluation route then commits `evaluating` before calling `EvaluationService`. On an exception it commits `evaluation_failed` and returns HTTP `503`, while the stored solution remains available for retry through the backend retry endpoint.

## 4. Structured Feedback

Feedback is represented as four categories:

- Strengths
- Issues
- Suggestions
- Trade-offs

This structure makes feedback easier to scan and gives the frontend predictable sections to render. It also avoids coupling the UI to one long LLM paragraph. The current implementation stores these lists as JSON and does not yet include severity, source, or confidence for individual items.

## 5. Avoiding Overengineering

The natural next step for a slow or unreliable evaluator could be a background worker, queue, or separate evaluation service. Those ideas were not added to this MVP because the assignment is centered on validating the learner loop, while those components would add deployment, coordination, and operational complexity.

This is a scope decision, not a claim that queues or separate services are never useful. If evaluation volume, latency, or reliability becomes a demonstrated problem, asynchronous processing would be a reasonable evolution. For the current repository, synchronous evaluation is easier to run and reason about.

## AI-Assisted Development Process

### Architecture

- Explored the evaluator contract and the separation between rule-based and LLM feedback.
- Considered attempt lifecycle states and the need to persist before calling an external service.
- Reviewed failure handling and retry as part of the learner workflow.

### Implementation

- Assisted with backend API and frontend workflow implementation decisions.
- Used source inspection and debugging reasoning to identify behavior at the API/service boundary.
- Kept implementation choices aligned with the existing FastAPI, SQLAlchemy, React, and Vite stack.

### Testing

- Identified validation cases such as an empty solution and an unknown problem.
- Reviewed gaps around evaluation failures, retry behavior, mocked external calls, and database isolation.

### Documentation

- Organized the project overview, architecture, setup, API surface, lifecycle, trade-offs, limitations, and AI usage into this single submission document.
- Verified claims against source files rather than documenting the intended design as if it were implemented.

## Key Engineering Lessons

1. Keep domain contracts separate from infrastructure-specific implementations.
2. Treat external evaluation services as failure-prone dependencies.
3. Persist user work before invoking an unreliable external service.
4. Use an abstraction when multiple evaluation strategies share a result contract.
5. Prefer simple architecture when additional infrastructure does not solve the current product problem.
6. Treat AI feedback as an evaluation signal, not absolute truth.
7. Keep feedback structured so it can evolve independently from the UI.
