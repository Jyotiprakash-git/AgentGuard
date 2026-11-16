import { useNavigate } from "react-router";
import { useAuth } from "../context/AuthContext";

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="header">
      <div>
        <strong>AgentGuard Workspace</strong>
        {/* <small>Interactive frontend demo</small> */}
      </div>

      <div className="header-actions">
        <span>
          {user.name} · {user.role}
        </span>
        <button onClick={handleLogout}>Switch account</button>
      </div>
    </header>
  );
}