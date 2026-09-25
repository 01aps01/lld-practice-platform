import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

function Practice() {
  const { problemId } = useParams();
  const navigate = useNavigate();

  const [problem, setProblem] = useState(null);
  const [solution, setSolution] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  // Load problem
  useEffect(() => {
    async function loadProblem() {
      try {
        const response = await fetch(
          `http://localhost:8000/problems/${problemId}`
        );

        if (!response.ok) {
          throw new Error("Problem not found");
        }

        const data = await response.json();

        setProblem(data);
      } catch (err) {
        setError(err.message);
      }
    }

    loadProblem();
  }, [problemId]);

  // Submit solution
  async function handleSubmit() {
    // Validate solution
    if (!solution.trim()) {
      setError(
        "Please write your solution before submitting."
      );
      return;
    }

    setSubmitting(true);
    setError("");

    try {
      // --------------------------------
      // 1. Save the attempt
      // --------------------------------

      const response = await fetch(
        "http://localhost:8000/attempts/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            problem_id: Number(problemId),
            solution: solution
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Submission failed"
        );
      }

      setSubmitted(true);

      // --------------------------------
      // 2. Evaluate the attempt
      // --------------------------------

      const evaluationResponse = await fetch(
        `http://localhost:8000/attempts/${data.id}/evaluate`,
        {
          method: "POST"
        }
      );

      // --------------------------------
      // 3. Evaluation failed
      // --------------------------------

      if (!evaluationResponse.ok) {
        console.log(
          "Evaluation failed, but submission was saved."
        );

        navigate(`/attempts/${data.id}`);

        return;
      }

      // --------------------------------
      // 4. Evaluation successful
      // --------------------------------

      navigate(`/attempts/${data.id}`);

    } catch (err) {
      setError(
        err.message || "Something went wrong."
      );
    } finally {
      setSubmitting(false);
    }
  }

  // Problem loading error
  if (error && !problem) {
    return (
      <div className="container">
        <h2>{error}</h2>

        <button
          onClick={() => navigate("/")}
        >
          Back to Problems
        </button>
      </div>
    );
  }

  // Loading
  if (!problem) {
    return (
      <div className="container">
        <p>Loading problem...</p>
      </div>
    );
  }

  return (
    <div className="container practice-page">

      {/* Back button */}
      <button
        className="back-button"
        onClick={() => navigate("/")}
      >
        ← Back
      </button>

      {/* Problem title */}
      <h1>{problem.title}</h1>

      {/* Problem description */}
      <div className="problem-description">

        <h2>Problem</h2>

        <p>
          {problem.description}
        </p>

        <h3>Requirements</h3>

        <ul>
          {problem.requirements.map(
            (requirement, index) => (
              <li key={index}>
                {requirement}
              </li>
            )
          )}
        </ul>

      </div>

      {/* Solution section */}
      <div className="solution-section">

        <h2>Your Solution</h2>

        <p>
          Describe your classes, interfaces,
          relationships, responsibilities and
          important design decisions.
        </p>

        <textarea
          value={solution}
          onChange={(e) =>
            setSolution(e.target.value)
          }
          placeholder={
            "Example:\n\nclass ParkingLot {...}\n\nclass ParkingSpot {...}\n\ninterface FeeCalculator {...}"
          }
          rows={20}
        />

        {/* Error */}
        {error && (
          <p className="error">
            {error}
          </p>
        )}

        {/* Submission message */}
        {submitted && (
          <p className="success">
            Submission saved. Evaluating your design...
          </p>
        )}

        {/* Submit button */}
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={submitting}
        >
          {submitting
            ? "Submitting & Evaluating..."
            : "Submit Solution"}
        </button>

      </div>
    </div>
  );
}

export default Practice;