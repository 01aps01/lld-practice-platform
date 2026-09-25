import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

function Attempt() {
  const { attemptId } = useParams();
  const navigate = useNavigate();

  const [attempt, setAttempt] = useState(null);
  const [problem, setProblem] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAttempt() {
      try {
        // Get the attempt
        const attemptResponse = await fetch(
          `http://localhost:8000/attempts/${attemptId}`
        );

        if (!attemptResponse.ok) {
          throw new Error("Attempt not found");
        }

        const attemptData = await attemptResponse.json();
        setAttempt(attemptData);

        // Get the problem associated with this attempt
        const problemResponse = await fetch(
          `http://localhost:8000/problems/${attemptData.problem_id}`
        );

        if (!problemResponse.ok) {
          throw new Error("Problem not found");
        }

        const problemData = await problemResponse.json();
        setProblem(problemData);
      } catch (err) {
        setError(err.message);
      }
    }

    loadAttempt();
  }, [attemptId]);

  // Error state
  if (error) {
    return (
      <div className="container">
        <h2>{error}</h2>

        <button onClick={() => navigate("/history")}>
          Back to History
        </button>
      </div>
    );
  }

  // Loading state
  if (!attempt || !problem) {
    return (
      <div className="container">
        <p>Loading attempt...</p>
      </div>
    );
  }

  return (
    <div className="container">
      <button onClick={() => navigate("/history")}>
        ← Back to History
      </button>

      <h1>{problem.title}</h1>

      {/* Attempt status */}
      <div className="status">
        Status: <strong>{attempt.status}</strong>
      </div>

      {/* Learner solution */}
      <h2>Your Solution</h2>

      <pre className="solution">
        {attempt.solution}
      </pre>

      {/* Feedback */}
      <div className="feedback-placeholder">
        <h2>Design Feedback</h2>

        {/* Evaluation is still running */}
        {attempt.status === "evaluating" && (
          <p>Your design is being evaluated...</p>
        )}

        {/* Evaluation failed */}
        {attempt.status === "evaluation_failed" && (
          <div>
            <p className="error">
              Evaluation failed, but your submission has been safely saved.
            </p>

            <button onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        )}

        {/* Evaluation succeeded */}
        {attempt.status === "evaluated" && attempt.feedback && (
          <>
            {/* Strengths */}
            <section className="feedback-section">
              <h3>Strengths</h3>

              {attempt.feedback.strengths?.length > 0 ? (
                <ul>
                  {attempt.feedback.strengths.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>No strengths identified.</p>
              )}
            </section>

            {/* Issues */}
            <section className="feedback-section">
              <h3>Issues</h3>

              {attempt.feedback.issues?.length > 0 ? (
                <ul>
                  {attempt.feedback.issues.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>No major issues identified.</p>
              )}
            </section>

            {/* Suggestions */}
            <section className="feedback-section">
              <h3>Suggestions</h3>

              {attempt.feedback.suggestions?.length > 0 ? (
                <ul>
                  {attempt.feedback.suggestions.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>No suggestions available.</p>
              )}
            </section>

            {/* Trade-offs */}
            <section className="feedback-section">
              <h3>Trade-offs</h3>

              {attempt.feedback.tradeoffs?.length > 0 ? (
                <ul>
                  {attempt.feedback.tradeoffs.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p>No trade-offs identified.</p>
              )}
            </section>
          </>
        )}

        {/* Fallback */}
        {attempt.status === "submitted" && (
          <p>
            Your submission has been saved. Evaluation has not started yet.
          </p>
        )}
      </div>
    </div>
  );
}

export default Attempt;