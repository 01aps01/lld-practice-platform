import {
  BrowserRouter,
  Routes,
  Route,
  Link
} from "react-router-dom";

import Home from "./pages/Home";
import Practice from "./pages/Practice";
import History from "./pages/History";
import Attempt from "./pages/Attempt";

function App() {
  return (
    <BrowserRouter>

      <nav className="navbar">

        <Link to="/">
          LLD Practice
        </Link>

        <Link to="/history">
          My Attempts
        </Link>

      </nav>

      <Routes>

        <Route
          path="/"
          element={<Home />}
        />

        <Route
          path="/practice/:problemId"
          element={<Practice />}
        />

        <Route
          path="/history"
          element={<History />}
        />

        <Route
          path="/attempts/:attemptId"
          element={<Attempt />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;