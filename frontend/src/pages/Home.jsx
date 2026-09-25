import { useEffect, useState } from "react";
import ProblemCard from "../components/ProblemCard";

function Home() {
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/problems/")
      .then((response) => response.json())
      .then((data) => {
        setProblems(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <p>Loading problems...</p>;
  }

  return (
    <div className="container">
      <h1>LLD Practice Platform</h1>

      <p className="subtitle">
        Practice Low-Level Design and improve your design skills.
      </p>

      <div className="problems">
        {problems.map((problem) => (
          <ProblemCard
            key={problem.id}
            problem={problem}
          />
        ))}
      </div>
    </div>
  );
}

export default Home;