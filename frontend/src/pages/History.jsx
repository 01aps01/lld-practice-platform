import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function History() {
  const [attempts, setAttempts] = useState([]);
  const [problems, setProblems] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    async function loadHistory() {
      try {
        const [attemptsResponse, problemsResponse] =
          await Promise.all([
            fetch("http://localhost:8000/attempts/"),
            fetch("http://localhost:8000/problems/")
          ]);

        const attemptsData =
          await attemptsResponse.json();

        const problemsData =
          await problemsResponse.json();

        const problemMap = {};

        problemsData.forEach((problem) => {
          problemMap[problem.id] = problem;
        });

        setAttempts(attemptsData);
        setProblems(problemMap);

      } catch (error) {
        console.error(error);
      }
    }

    loadHistory();
  }, []);

  return (
    <div className="container">

      <button onClick={() => navigate("/")}>
        ← Problems
      </button>

      <h1>My Attempts</h1>

      {attempts.length === 0 ? (
        <p>
          You haven't submitted any solutions yet.
        </p>
      ) : (
        <div className="history-list">

          {attempts.map((attempt) => (

            <div
              key={attempt.id}
              className="history-card"
            >

              <h2>
                {problems[attempt.problem_id]?.title ||
                  "Unknown Problem"}
              </h2>

              <p>
                Status: <strong>
                  {attempt.status}
                </strong>
              </p>

              <p>
                Submitted:{" "}
                {new Date(
                  attempt.created_at
                ).toLocaleString()}
              </p>

              <button
                onClick={() =>
                  navigate(`/attempts/${attempt.id}`)
                }
              >
                View Attempt
              </button>

            </div>

          ))}

        </div>
      )}

    </div>
  );
}

export default History;