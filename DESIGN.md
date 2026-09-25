# LLD Practice Platform - Design Note

## 1. Design Objective

The MVP helps a learner practice an LLD problem, submit a textual design, receive explainable feedback, and review the saved attempt. The design prioritizes clear responsibilities, persisted learner work, an evaluator that can change independently of the API, and practical failure handling.

The target loop is:

```text
Choose -> Practice -> Submit -> Evaluate -> Review -> Retry
```

The implementation uses a React frontend and a small FastAPI backend backed by SQLite. It is intentionally a simple monolith for a two-day assignment.

## 2. MVP User Flow

### 1. Select Problem

The home page requests `GET /problems/` and renders the available problem cards. The current seed data contains Parking Lot, Vending Machine, and Elevator System.

### 2. Start Practice

The learner navigates to `/practice/:problemId`. The practice page loads the problem description and requirements and provides a text area for the solution.

### 3. Submit

The frontend validates that the text is not blank, then calls `POST /attempts/`. The backend verifies the problem exists, rejects whitespace-only solutions, and commits the attempt with status `submitted`.

### 4. Evaluate

The frontend calls `POST /attempts/{attempt_id}/evaluate`. The API changes the status to `evaluating`, commits that state, and invokes `EvaluationService`.

### 5. Review Feedback

Successful evaluation stores four feedback lists: strengths, issues, suggestions, and trade-offs. The attempt page displays those categories along with the original solution.

### 6. View History / Retry

The history page calls `GET /attempts/` and shows attempts newest first. The backend exposes `POST /attempts/{attempt_id}/retry-evaluation` for `evaluation_failed` or `submitted` attempts. The current frontend displays a “Try Again” button for a failed attempt, but that button reloads the page rather than calling the retry endpoint; this is an implementation gap rather than a completed end-to-end retry flow.

```text
React pages
    |
    +--> GET problems --> choose problem --> write text solution
						   |
						   v
					   POST attempt
						   |
						   v
					   POST evaluate
					   /          \
					  v            v
				  evaluated     evaluation_failed
					  |            |
					  v            v
				   review/history  retry API
```

## 3. High-Level Architecture

```text
React + React Router
	 |
	 v
FastAPI routers
	 |
	 +--> SQLAlchemy models --> SQLite
	 |
	 +--> EvaluationService
		  |
		  +--> RuleBasedEvaluator
		  |
		  +--> LLMEvaluator --> Google Gemini API
```

- **Frontend:** `App.jsx` defines routes for home, practice, history, and attempt details. Pages use `fetch` against the local API.
- **API:** `problems.py` handles problem retrieval. `attempts.py` handles creation, retrieval, evaluation, and retry.
- **Schemas:** Pydantic models define attempt input and problem/attempt responses.
- **Persistence:** SQLAlchemy models store problems and attempts in SQLite. Requirements and feedback are serialized as JSON text.
- **Services:** Evaluators contain evaluation behavior; `EvaluationService` combines their results.
- **External dependency:** `LLMEvaluator` calls Google Gemini using `GEMINI_API_KEY`.

## 4. Why a Monolith?

A single FastAPI backend with a separate React development process is appropriate for this assignment:

- it is easy to run locally;
- request flow is easy to trace;
- the database and service boundaries remain visible;
- testing and iteration have low operational overhead; and
- the main product risk is whether the learner feedback loop is useful, not whether the system can distribute work across services.

The trade-off is that the API owns a synchronous Gemini call, so evaluation latency and external availability affect the request. A larger product could move evaluation to a background worker, but that would add coordination and operational complexity before the MVP has demonstrated the need.

## 5. Domain Model

### `Problem`

The domain dataclass represents an LLD prompt with `id`, `title`, `description`, and `requirements`. Its responsibility is to provide enough context for a meaningful attempt. `ProblemModel` is the SQLAlchemy persistence representation; the API converts the JSON-encoded requirements column into a list for responses.

### `Attempt`

The domain dataclass represents the learner's submission with `id`, `problem_id`, `solution`, `status`, optional `feedback`, and `created_at`. Its responsibility is to preserve the learner's work and evaluation state. `AttemptModel` stores the same information in SQLite. The current database model does not define a foreign key or ORM relationship to `ProblemModel`; routes perform the problem lookup explicitly.

### `AttemptStatus`

The domain enum defines `draft`, `submitted`, `evaluating`, `evaluated`, and `failed`. The current API creates `submitted`, `evaluating`, and `evaluated`, and persists `evaluation_failed` when evaluation fails. Therefore, `failed` in the domain enum and `evaluation_failed` in the API are inconsistent. `draft` is defined but is not produced by the current API.

### `EvaluationResult`

This dataclass is the shared result shape for an evaluator. It contains lists for `strengths`, `issues`, `suggestions`, and `tradeoffs`. Keeping this shape separate from the API response lets service implementations return common feedback without knowing how it will be rendered.

## 6. Evaluator Abstraction

```text
Evaluator
├── RuleBasedEvaluator
└── LLMEvaluator
```

`Evaluator` is an abstract class with `evaluate(problem, solution) -> EvaluationResult`. The API depends on `EvaluationService`, not directly on Gemini. This separates the decision to evaluate an attempt from the mechanism used to produce feedback.

`RuleBasedEvaluator` performs small deterministic text checks: solution length, the presence of `interface`, and the presence of `class`. It also adds general responsibility-separation and abstraction guidance. It does not parse a class diagram or prove design correctness.

`LLMEvaluator` loads the Gemini key, sends a prompt requesting JSON, and tries the configured Gemini model names in sequence when calls fail. A future implementation could add another LLM provider, a problem-specific evaluator, static analysis, or human review by implementing the same contract. Those are extension options, not current features.

## 7. EvaluationService

`EvaluationService` is the orchestration layer. It constructs `RuleBasedEvaluator` and `LLMEvaluator`, invokes both with the problem context and solution, and concatenates each corresponding feedback list into one `EvaluationResult`.

Keeping this coordination out of the API route is useful because the route should manage HTTP validation, database state, and response mapping. Evaluation policy can change independently. The current service does not score results, resolve disagreements, or fall back to the rule-based result if LLM construction or evaluation fails.

## 8. Evaluation Strategy

The evaluator is designed for open-ended LLD rather than one fixed answer. The Gemini prompt explicitly says that multiple valid solutions may exist and asks for concrete reasons and actionable feedback.

The LLM is asked to consider:

- responsibility distribution;
- SOLID principles;
- coupling and cohesion;
- abstraction and interfaces;
- extensibility;
- appropriate design patterns;
- missing requirements explicitly stated in the problem;
- potential design problems; and
- trade-offs.

These dimensions describe review areas, not a guaranteed objective score. The deterministic evaluator adds predictable basic observations, while the LLM provides broader reasoning. `EvaluationService` combines the text results without claiming that either source is absolute truth.

## 9. Deterministic vs LLM Evaluation

| Evaluation Type | Good For | Limitation |
|---|---|---|
| Deterministic checks | Fast, repeatable checks for basic solution detail and textual indicators | The current checks are shallow heuristics and do not understand the design model |
| LLM review | Contextual discussion of responsibilities, abstractions, requirements, and trade-offs | Depends on Gemini, adds latency, may vary between calls, and can produce incorrect advice |

The hybrid approach gives the learner stable baseline observations plus broader review. It is not a formal grading system. In the current implementation, the LLM is still required by `EvaluationService`; the rule-based result is not a fallback when Gemini is unavailable.

## 10. Submission and Evaluation Lifecycle

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

The attempt is committed as `submitted` before the frontend asks for evaluation. The evaluation route commits `evaluating` before invoking the external service. On success it serializes feedback and commits `evaluated`. On an exception it commits `evaluation_failed` and returns HTTP `503`.

Persisting first means a Gemini outage or malformed response cannot erase the solution. The learner's work remains available through the attempt and history endpoints.

## 11. Failure Handling

`LLMEvaluator` raises when no API key is configured or when all configured Gemini model attempts fail. The attempt route catches evaluation exceptions, retains the solution, sets `evaluation_failed`, and reports a temporary service failure.

The retry route accepts only `evaluation_failed` and `submitted` attempts, changes the state to `evaluating`, and repeats the same evaluation process. This provides a backend recovery path without creating a new submission. The frontend currently does not connect its failed-attempt button to this endpoint, so the recovery path is not fully exposed in the UI.

## 12. Extensibility

### Evaluation approaches

The `Evaluator` contract supports another implementation without changing the basic service result shape. Possible future implementations include another LLM provider, a problem-specific ruleset, static analysis, or human review. `EvaluationService` would need policy changes if those evaluators should be selected conditionally, weighted, or used as fallbacks.

### Submission formats

The current format is a plain text solution sent as `AttemptCreate.solution`. Future formats such as code, UML/image diagrams, or structured JSON would require explicit modeling rather than treating every submission as one string. Likely changes would include:

- a submission type and corresponding stored payload;
- format-specific validation;
- evaluator input adapters;
- frontend components appropriate to the format; and
- updated API schemas and tests.

None of these formats is implemented in the current repository.

## 13. API Design

| Method | Endpoint | Responsibility |
|---|---|---|
| `GET` | `/` | Return an API-running message |
| `GET` | `/health` | Return a basic health response |
| `GET` | `/problems/` | List available problems |
| `GET` | `/problems/{problem_id}` | Retrieve one problem |
| `POST` | `/attempts/` | Validate and persist a solution |
| `GET` | `/attempts/` | List attempts newest first |
| `GET` | `/attempts/{attempt_id}` | Retrieve one attempt |
| `POST` | `/attempts/{attempt_id}/evaluate` | Evaluate an attempt |
| `POST` | `/attempts/{attempt_id}/retry-evaluation` | Retry a submitted or failed evaluation |

Missing problem and attempt resources return `404`. Empty submissions return `400`. Evaluation failures return `503` after preserving the attempt.

## 14. Persistence Design

The backend uses SQLite through SQLAlchemy with the database URL `sqlite:///./lld_platform.db`. Tables are created during application import. `ProblemModel` stores problem metadata and JSON-encoded requirements. `AttemptModel` stores the solution, problem ID, status, JSON-encoded feedback, and creation time.

Persistence is needed for history and for recovery after evaluation failure. SQLite is sufficient for a local MVP because it avoids a separate database service and the assignment does not require multi-instance deployment. Migrations, backups, user ownership, and production concurrency controls are not implemented.

## 15. Testing Strategy

The backend suite contains five endpoint tests:

- successful problem listing;
- successful retrieval of the seeded Parking Lot problem;
- missing problem returns `404`;
- empty solution returns `400`; and
- submission with an invalid problem returns `404`.

These tests cover the problem retrieval path and the main submission validation boundaries. The suite does not currently test evaluation success/failure, retry behavior, attempt listing/detail endpoints, Gemini fallback behavior, seed idempotency, database isolation, or frontend behavior. The tests use the application's local SQLite state rather than isolated fixtures.

## 16. Key Design Trade-offs

### Text Submission vs Diagram Editor

**Decision:** Use a text area for the MVP.

**Reason:** Text supports classes, interfaces, relationships, and design decisions with little frontend complexity, which allows the submission and feedback loop to be tested quickly.

**Trade-off:** Learners cannot create or inspect a visual class diagram, and the evaluator receives unstructured text.

**Future option:** Add a diagram or structured model after the text workflow is validated.

### SQLite vs PostgreSQL

**Decision:** Use SQLite.

**Reason:** It keeps local setup small and is adequate for a single-process assignment prototype.

**Trade-off:** The repository does not address production concurrency, migrations, backups, or multi-user isolation.

**Future option:** Move to a server database if deployment and multi-user requirements justify it.

### Synchronous vs Background Evaluation

**Decision:** Evaluate synchronously in the API request.

**Reason:** It is simpler to implement and gives a direct result for the MVP.

**Trade-off:** Gemini latency and availability affect the evaluation request.

**Future option:** Persist a job state and process evaluation asynchronously if latency becomes a demonstrated problem.

### Deterministic + LLM vs LLM-only

**Decision:** Run both evaluators and combine their lists.

**Reason:** Deterministic checks are predictable, while an LLM can discuss open-ended design qualities.

**Trade-off:** The two sources are not reconciled, and the current service still fails if the LLM is unavailable.

**Future option:** Make deterministic feedback available independently or use it as a true fallback.

### Monolith vs Distributed Services

**Decision:** Keep the backend as one FastAPI application.

**Reason:** The assignment is focused on domain behavior and the learner loop, not independent service scaling.

**Trade-off:** API, persistence, and evaluation concerns share one deployable process.

**Future option:** Split evaluation only when operational or scaling needs are real.

## 17. Security / Configuration

`LLMEvaluator` reads `GEMINI_API_KEY` from the environment, with `python-dotenv` loading a local `.env` file. `.env` is excluded in `.gitignore` and real keys must not be committed. CORS is configured for `http://localhost:5173`.

There is no authentication or authorization. The API should therefore remain a local development service until those controls and user ownership are added.

## 18. Limitations

- No authentication, users, or per-user attempt ownership.
- Text-only submissions with no diagram editor or code execution.
- Basic deterministic text heuristics rather than design parsing.
- External Gemini dependency for the current evaluation service.
- Synchronous evaluation and no background worker.
- No numeric score or evaluator confidence model.
- No frontend tests.
- Tests depend on existing local SQLite data.
- Frontend retry UI does not call the implemented retry endpoint.
- Domain status `failed` does not match persisted API status `evaluation_failed`.
- No production observability, migrations, backups, or deployment controls.

These are conscious boundaries for the two-day MVP, not claims of production readiness.

## 19. Future Improvements

### Learner Experience

- Connect the failed-attempt button to `retry-evaluation` and show retry progress.
- Add attempt comparison so learners can review changes between submissions.
- Add diagram or structured submission support.

### Evaluation

- Make evaluator selection or fallback explicit.
- Normalize status values across domain, persistence, and API layers.
- Add mocked evaluator tests and richer feedback metadata such as evidence or severity.
- Calibrate feedback against a small set of reviewed examples before introducing scores.

### Platform

- Isolate tests with fixtures and a test database.
- Add authentication and user-owned attempts.
- Add migrations and a server database if deployment needs require them.
- Move long-running evaluation to background processing when synchronous latency is no longer acceptable.

## 20. Final Design Summary

The MVP uses a small domain model centered on problems and persisted attempts. FastAPI routes handle HTTP and state transitions, SQLAlchemy handles SQLite persistence, and `EvaluationService` coordinates a shared evaluator abstraction with deterministic and Gemini-backed implementations. Attempts are saved before evaluation so external failure is recoverable. The design leaves room for new evaluators and submission formats while keeping the current system small enough to validate the core practice loop in two days.
