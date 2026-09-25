import { useNavigate } from "react-router-dom";

function ProblemCard({ problem }) {
  const navigate = useNavigate();

  return (
    <div className="problem-card">
      <h2>{problem.title}</h2>

      <p>{problem.description}</p>

      <h3>Requirements</h3>

      <ul>
        {problem.requirements.map((requirement, index) => (
          <li key={index}>{requirement}</li>
        ))}
      </ul>

      <button
        onClick={() => navigate(`/practice/${problem.id}`)}
      >
        Practice
      </button>
    </div>
  );
}

export default ProblemCard;