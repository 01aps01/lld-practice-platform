# LLD Practice Platform - Research Note

## 1. Research Objective

This research considers how developers currently practice Low-Level Design, how they validate an open-ended design, and why improvement is difficult without feedback on their own work. The goal is to identify a small product direction that supports repeated practice without turning a two-day assignment into a large learning platform.

## 2. Learner Problem

Most LLD practice starts with a prompt such as Parking Lot, Vending Machine, or Elevator System. The learner writes classes and relationships, then compares the result with a tutorial, interview guide, or reference solution. That process answers whether the learner can produce *a* design, but not necessarily whether the responsibilities are well placed or how the design could improve.

LLD is difficult to evaluate because there is rarely one correct implementation. Two designs can satisfy the same requirements while making different choices about abstractions, ownership, patterns, and extensibility. Useful review therefore needs to discuss:

- responsibility boundaries;
- coupling and cohesion;
- abstraction and interface choices;
- extensibility and design patterns;
- requirements that were missed; and
- trade-offs introduced by making a design simpler or more flexible.

The learner's real need is an iterative loop: submit a design, understand what was strong or weak, review the original work, and try again. A question bank alone does not provide that loop.

## 3. Existing Approaches

The following comparison is based on the observable interaction models of common developer-learning tools and resources, not on user interviews or fabricated usage data.

### Coding Practice Platforms

Platforms such as LeetCode, HackerRank, and CodeSignal are effective at presenting a problem, accepting a submission, and returning objective or test-based results. Their model works especially well when correctness can be checked against expected outputs, constraints, or hidden tests.

That model does not transfer cleanly to LLD. A class design is usually text or a diagram, and there may be several valid solutions. Automated checks can verify basic structure or required behavior, but they cannot by themselves explain why responsibility distribution or an abstraction boundary is weak.

### Interview Preparation Resources

LLD tutorials, interview guides, solution repositories, and discussion articles provide useful prompts, vocabulary, and example designs. They are good references when a learner needs to study a pattern or compare alternative approaches.

Their limitation is that feedback is usually attached to the published solution rather than to the learner's submitted attempt. The learner must perform the comparison manually, and the resource does not necessarily preserve a history of revisions or make the next practice step explicit.

### Diagramming and Design Tools

UML and general diagramming tools help learners express classes, relationships, and dependencies visually. They address representation and communication, which are important parts of design practice.

They do not normally evaluate whether the design meets the stated requirements, whether responsibilities are cohesive, or which trade-offs should be reconsidered. A diagram editor would also add interaction and persistence work before the feedback loop itself is validated.

### AI-Assisted Learning

An LLM can review open-ended design text and provide reasoning-oriented comments about coupling, cohesion, SOLID principles, interfaces, extensibility, missing requirements, and trade-offs. This makes it a useful complement to deterministic checks for a prototype.

It is not an objective judge. Results can vary, calls can be slow or unavailable, and the model may produce incomplete or inconsistent advice. The prompt must constrain the evaluation, ask for structured output, and avoid treating one architecture as universally correct. The repository uses Google Gemini for this purpose and keeps a small deterministic evaluator alongside it.

## 4. Comparison Table

| Approach | Strength | Limitation for LLD Practice |
|---|---|---|
| Coding practice platforms | Clear submission and automated result loop | Assumes correctness can be checked more objectively than most LLD designs |
| Interview resources | Strong explanations, examples, and design vocabulary | Feedback is generally about a reference solution, not the learner's saved attempt |
| Diagramming tools | Good representation of classes and relationships | Expresses a design but does not inherently review its quality or trade-offs |
| LLM-assisted review | Can provide contextual, reasoning-oriented feedback on open-ended text | External dependency, latency, non-determinism, and possible hallucinations |

## 5. Key Gaps

The traditional flow is often:

```text
Problem -> Design -> Read a reference solution
```

The more useful practice loop is:

```text
Problem -> Design -> Submit -> Feedback -> Review -> Retry
```

The gap is not simply a shortage of LLD questions. The larger gap is a structured review of the learner's own design. Feedback must remain useful when several designs are valid: it should explain what the design does well, identify a concrete concern, give a possible improvement, and make the trade-off visible. It should not reduce the result to a pass/fail comparison with one predetermined class diagram.

## 6. Product Direction

The MVP direction is a focused practice workspace with a small problem library, explicit requirements, text submission, persisted attempts, structured evaluation, and attempt history. The target flow is:

```text
Problem Selection -> Practice -> Submission -> Evaluation -> Feedback -> History -> Retry
```

This is a better two-day boundary than a complete LMS, social features, complex account management, collaboration, or distributed infrastructure. It tests whether the feedback loop is useful before adding features that do not answer the core learner problem.

## 7. Product Principles

### Multiple valid solutions

Review design qualities and reasoning rather than comparing every submission with one fixed answer.

### Actionable feedback

Separate strengths, issues, suggestions, and trade-offs so the learner can understand both the current design and the next improvement.

### Preserve learner work

Persist a submission before calling an external evaluator. An AI outage should produce a recoverable evaluation failure, not data loss.

### Extensible evaluation

Use a shared evaluator contract so deterministic checks and LLM review can evolve independently and another strategy can be added later.

### Scope discipline

Validate the learner loop with a simple monolith before introducing queues, background workers, or production-scale platform concerns.

## 8. MVP Scope

### In Scope

- Three seeded LLD problems: Parking Lot, Vending Machine, and Elevator System.
- Problem descriptions and requirement lists.
- A React text-based practice screen.
- Persisted submissions and attempt history in SQLite.
- Attempt statuses for submission, evaluation, success, and evaluation failure.
- Basic deterministic checks through `RuleBasedEvaluator`.
- Structured Google Gemini feedback through `LLMEvaluator`.
- A combined `EvaluationService` and backend retry endpoint.
- Backend tests for problem retrieval and submission validation.

### Out of Scope

- Authentication, user accounts, and per-user history.
- Diagram editing, code execution, and structured diagram submission.
- Numeric scoring or a calibrated evaluation rubric.
- Frontend test coverage and production observability.
- Background evaluation, queues, multi-instance deployment, and large-scale infrastructure.

## 9. Research Conclusion

The product direction is not another static LLD question bank. It is a small, feedback-driven practice loop around the learner's own design. The current implementation is intentionally narrow: text is enough to validate submission, persistence, structured review, and history first; richer submission formats and more reliable evaluation can be added once that loop proves useful.
