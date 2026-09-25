# LLD Practice Platform

A focused MVP for practicing Low-Level Design (LLD) problems through a
structured learning loop:

> Choose a problem → Design a solution → Submit → Get feedback → Review → Retry

The platform is designed around one core idea: LLD practice should not end
with submitting a design. Learners should be able to understand what was
good, what could be improved, what trade-offs they made, and then try again.

---

## 1. Product Goal

LLD practice often relies on static interview questions, reference solutions,
or manual feedback. This makes it difficult for a learner to repeatedly
practice and receive structured feedback on their own design decisions.

This MVP focuses on closing that loop.

### Learner flow

1. Browse available LLD problems.
2. Select a problem.
3. Read its requirements.
4. Write a design solution.
5. Submit the solution.
6. Receive structured design feedback.
7. Review the attempt later.
8. Retry the problem or evaluation.

The MVP intentionally focuses on this core loop rather than building a
large learning management system.

---

# 2. Features

### Problem Practice

- Browse LLD problems.
- View problem descriptions and requirements.
- Practice problems such as:
  - Parking Lot
  - Vending Machine
  - Elevator System

### Attempt Management

- Submit a solution for a problem.
- Persist every attempt.
- Track attempt status.
- View previous attempts.
- Re-open an individual attempt.

### Design Evaluation

The platform combines:

- Deterministic rule-based checks.
- LLM-based design analysis.

Feedback is structured into:

- Strengths
- Issues
- Suggestions
- Trade-offs

### Failure Handling

If AI evaluation fails:

- The learner's submission remains saved.
- The attempt is marked as `evaluation_failed`.
- The learner can retry evaluation.

This means an external AI/API failure does not result in data loss.

---

# 3. Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Google Gemini API
- pytest

## Frontend

- React
- Vite
- React Router
- CSS

---

# 4. Architecture

The application is intentionally implemented as a simple monolith for the
MVP.

```text
                     ┌─────────────────────┐
                     │    React Frontend   │
                     │                     │
                     │ Problems             │
                     │ Practice             │
                     │ Attempts / History   │
                     └──────────┬──────────┘
                                │
                           HTTP / REST
                                │
                                ▼
                     ┌─────────────────────┐
                     │    FastAPI Backend  │
                     │                     │
                     │ Problem API         │
                     │ Attempt API         │
                     │ Evaluation Service  │
                     └──────────┬──────────┘
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
             SQLite      RuleBasedEvaluator  LLMEvaluator
                                              │
                                              ▼
                                         Gemini API
Why a monolith?

The assignment is focused on the learner experience and LLD evaluation
rather than distributed infrastructure.

A monolithic backend keeps the MVP:

Easy to run locally.
Easy to understand.
Easy to test.
Easy to extend.

Introducing queues, microservices, Kubernetes, or separate evaluation
workers would add operational complexity without providing meaningful value
for this MVP.

5. Project Structure
lld-practice-platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── attempts.py
│   │   │   └── problems.py
│   │   │
│   │   ├── models/
│   │   │   ├── database_models.py
│   │   │   └── domain.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── attempt.py
│   │   │   └── problem.py
│   │   │
│   │   ├── services/
│   │   │   ├── evaluator.py
│   │   │   └── evaluation_service.py
│   │   │
│   │   ├── database.py
│   │   ├── main.py
│   │   └── seed.py
│   │
│   ├── tests/
│   │   ├── test_problems.py
│   │   └── test_attempts.py
│   │
│   ├── .env
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ProblemCard.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Practice.jsx
│   │   │   ├── History.jsx
│   │   │   └── Attempt.jsx
│   │   │
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   └── package.json
│
├── DESIGN.md
├── RESEARCH.md
└── README_AI_USAGE.md
6. Core Domain Model

The MVP has two primary domain concepts.

Problem

Represents an LLD problem that a learner can practice.

Problem
├── id
├── title
├── description
└── requirements
Attempt

Represents a learner's submission for a problem.

Attempt
├── id
├── problem_id
├── solution
├── status
├── feedback
└── created_at
Attempt lifecycle
submitted
     │
     ▼
evaluating
     │
     ├──────────────► evaluated
     │
     └──────────────► evaluation_failed
                              │
                              ▼
                     retry evaluation

Persisting the attempt independently from evaluation is an important design
choice because evaluation is an external dependency.

7. Evaluation Design

A major design question was:

How can the platform provide useful feedback when multiple LLD solutions
can be valid?

The system deliberately avoids comparing a learner's answer against one
"correct" class diagram.

Instead, the evaluation focuses on design qualities.

The evaluator considers:

Responsibility distribution.
SOLID principles.
Coupling and cohesion.
Abstraction and interfaces.
Extensibility.
Appropriate use of design patterns.
Missing requirements.
Potential design problems.
Trade-offs.

The evaluator is instructed not to recommend design patterns simply for the
sake of using patterns and not to assume that there is only one valid
architecture.

8. Evaluator Abstraction

The backend defines an Evaluator abstraction.

Conceptually:

Evaluator
    │
    ├── RuleBasedEvaluator
    │
    └── LLMEvaluator

Both evaluators follow the same evaluation contract.

This makes it possible to introduce additional evaluation strategies later
without coupling the API layer directly to a specific evaluation provider.

The EvaluationService combines the available evaluation signals into the
feedback returned to the learner.

9. Why Deterministic + LLM Evaluation?

LLMs are useful for reasoning about design quality, but relying entirely on
an LLM introduces several problems:

Non-deterministic responses.
External API failures.
Potentially inconsistent feedback.
Difficulty enforcing basic validation.

Therefore the MVP uses a hybrid approach.

Deterministic evaluation

Useful for predictable checks such as:

Whether the submission contains meaningful content.
Whether classes/interfaces are discussed.
Whether basic design concepts are present.
LLM evaluation

Useful for higher-level reasoning such as:

Responsibility distribution.
Coupling/cohesion.
Extensibility.
Trade-offs.
Potential design smells.

This separation also makes the evaluation layer easier to evolve.

10. API Overview
Problems
GET /problems/

Returns available practice problems.

GET /problems/{problem_id}

Returns a specific problem.

Attempts
POST /attempts/

Creates a new attempt.

GET /attempts/

Returns attempt history.

GET /attempts/{attempt_id}

Returns an individual attempt.

Evaluation
POST /attempts/{attempt_id}/evaluate

Evaluates an attempt.

POST /attempts/{attempt_id}/retry-evaluation

Retries evaluation when the previous evaluation failed.

11. Local Setup
Prerequisites

Install:

Python 3.11+
Node.js 18+
npm

A Gemini API key is required for AI evaluation.

Backend Setup

From the project root:

cd backend

Create a virtual environment:

python -m venv venv

Activate it on Windows PowerShell:

.\venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Create:

backend/.env

Add:

GEMINI_API_KEY=your_api_key_here

Start the backend:

uvicorn app.main:app --reload

Backend:

http://localhost:8000

Swagger API documentation:

http://localhost:8000/docs
Frontend Setup

Open another terminal.

From the project root:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Frontend:

http://localhost:5173
12. Running Tests

From the backend directory:

pytest

The tests cover important behaviour including:

Problem retrieval.
Missing problem handling.
Empty solution rejection.
Invalid problem submission.

The tests intentionally focus on core API behaviour and failure cases
relevant to the MVP.

13. Data Persistence

SQLite is used for the MVP.

The database stores:

Problems.
Attempts.
Submission status.
Evaluation feedback.
Creation timestamps.

SQLite was selected because it provides persistence without requiring an
additional database server.

For a production deployment, PostgreSQL or another managed relational
database would be a natural next step.

14. Error and Failure Handling

The system treats evaluation as an external dependency.

Before evaluation:

Submission
   ↓
Persist Attempt
   ↓
Start Evaluation

If evaluation succeeds:

evaluated

If evaluation fails:

evaluation_failed

The original submission remains available.

The learner can retry evaluation without having to rewrite the solution.

This was chosen because preserving learner work is more important than
making the evaluation path completely synchronous or failure-free.

15. Security / Configuration

API keys are loaded from environment variables.

The .env file should never be committed to Git.

The repository's .gitignore excludes:

.env
venv/
__pycache__/
node_modules/
dist/

Do not share or commit your actual Gemini API key.

16. Limitations

This is an MVP and intentionally does not implement:

Authentication.
Multiple user accounts.
Role-based access.
Advanced diagram editing.
Code execution.
Real-time collaboration.
Sophisticated numerical scoring.
Background job infrastructure.
Production-grade observability.
Advanced AI evaluation calibration.

The current product is focused on validating the core practice loop.

17. Future Improvements

Potential next steps include:

Learning experience
Difficulty levels.
More LLD problems.
Hints.
Problem categories.
Progress tracking.
Comparison between attempts.
"Improve this design" guided retries.
Evaluation
More deterministic design checks.
Evaluation rubrics per problem.
Confidence indicators.
Better consistency checks across LLM evaluations.
Versioned evaluator prompts.
Background evaluation for long-running requests.
Platform
Authentication.
User profiles.
PostgreSQL.
Analytics.
Production deployment.
Rate limiting.
Observability and structured logging.
18. Out of Scope for the MVP

The following were deliberately excluded:

Microservices
Message queues
Kubernetes
Complex distributed architecture
Real-time collaboration
Full LMS functionality
Advanced diagram editor

The reason is simple: the assignment's primary goal is a demonstrable
LLD practice experience, not infrastructure complexity.

AI_USAGE.md
AI Usage Report

AI tools were used as an engineering assistant during the development of
this project.

The important principle was to use AI for exploration, implementation
assistance, debugging, and review while keeping architectural decisions
aligned with the assignment requirements and reviewing the generated code.

1. Evaluator Abstraction
Problem

The platform needs to support different ways of evaluating an LLD solution.

AI-assisted suggestion

Introduce an evaluator abstraction with a common interface.

Decision

Accepted.

The project defines an Evaluator abstraction and provides concrete
implementations such as:

Evaluator
├── RuleBasedEvaluator
└── LLMEvaluator
Why

This keeps the evaluation mechanism separate from the API layer and allows
future evaluators to be introduced without rewriting the attempt workflow.

2. Hybrid Deterministic + LLM Evaluation
Problem

LLD solutions are open-ended and multiple designs can be valid.

A purely rule-based evaluator would be too rigid, while a purely
LLM-based evaluator could be inconsistent and dependent on an external API.

AI-assisted suggestion

Combine deterministic checks with LLM reasoning.

Decision

Accepted.

The MVP uses:

RuleBasedEvaluator
       +
LLMEvaluator
       ↓
EvaluationService
       ↓
Structured Feedback
Why

This provides predictable baseline validation while allowing an LLM to
reason about higher-level design concepts.

3. Persist Before Evaluation
Problem

AI evaluation can fail because of:

API errors.
Capacity issues.
Network problems.
Unexpected provider failures.
AI-assisted suggestion

Save the learner's submission before invoking the evaluator.

Decision

Accepted.

The system first persists the attempt and then starts evaluation.

If evaluation fails, the attempt remains stored as:

evaluation_failed

The learner can retry evaluation later.

Why

The learner's work should not depend on the availability of an external
AI service.

4. Structured Feedback
Problem

A single block of generated feedback would be difficult for a learner to
scan and difficult for the frontend to present consistently.

AI-assisted suggestion

Return structured feedback categories.

Decision

Accepted.

The feedback model contains:

Strengths
Issues
Suggestions
Trade-offs
Why

This makes feedback actionable and gives the learner a clear path from
understanding the problem to improving the design.

5. Avoid Overengineering the MVP
Problem

The evaluation system could theoretically be implemented using:

Background workers.
Message queues.
Separate evaluation services.
Distributed infrastructure.
AI-assisted suggestion

Consider asynchronous/background processing if evaluation becomes slow.

Decision

Rejected for the current MVP.

The implementation remains a simple FastAPI monolith with synchronous
evaluation.

Why

The assignment prioritizes the learner experience and demonstrable
end-to-end workflow.

Adding distributed infrastructure would increase implementation and
operational complexity without being necessary to validate the core idea.

A future production version could introduce background evaluation if
evaluation latency becomes significant.

AI-Assisted Development Process

AI assistance was used in several areas:

Architecture
Exploring evaluator abstractions.
Thinking through deterministic vs LLM evaluation.
Designing attempt lifecycle states.
Considering failure handling.
Implementation
Generating implementation starting points.
Assisting with FastAPI endpoints.
Assisting with React components.
Debugging integration issues.
Testing
Identifying important API behaviours.
Suggesting failure and edge cases.
Documentation
Structuring the README.
Reviewing trade-offs and limitations.
Organizing the AI usage report.

Generated suggestions were reviewed and adapted to the actual MVP rather
than being accepted blindly.

Key Engineering Lessons

The development process highlighted several practical engineering
principles:

Separate domain concerns from infrastructure.
Design external dependencies to fail gracefully.
Persist user work before calling unreliable external services.
Use abstractions where multiple implementations are expected.
Prefer simple architecture when complexity does not solve the core
product problem.
Treat AI output as one evaluation signal rather than absolute truth.
Keep feedback structured so it can evolve independently from the UI.
