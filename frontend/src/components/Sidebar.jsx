// import { NavLink } from "react-router";
import { Shield } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { Link, NavLink } from "react-router";
// import { Link, NavLink } from "react-router";
// import { Shield } from "lucide-react";
// import { useAuth } from "../context/AuthContext";

const navigation = {
  user: [
    ["Overview", "overview"],
    ["Agent Playground", "playground"],
    ["My Activity", "activity"],
    ["My Approvals", "approvals"],
  ],
  analyst: [
    ["Overview", "overview"],
    ["Activity Monitor", "activity"],
    ["Security Alerts", "alerts"],
  ],
  admin: [
    ["Overview", "overview"],
    ["Users & Roles", "users"],
    ["Policies", "policies"],
    ["Approvals", "approvals"],
    ["Agents & Tools", "agents"],
  ],
};

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="sidebar">
      <Link
  to={`/${user.role}/overview`}
  className="brand"
  aria-label="Go to dashboard home"
  title="Go to dashboard home"
>
  <Shield size={30} />

  <div>
    <strong>AgentGuard OS</strong>
    <small>AI SECURITY CONSOLE</small>
  </div>
</Link>

      <p className="nav-label">{user.role.toUpperCase()} MODULE</p>

      <nav>
        {navigation[user.role].map(([label, path]) => (
          <NavLink
            key={path}
            to={`/${user.role}/${path}`}
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>

      {/* <p className="sidebar-footer">Permissions before execution.</p> */}
    </aside>
  );
}