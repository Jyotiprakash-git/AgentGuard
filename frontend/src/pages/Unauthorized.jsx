import { Link } from "react-router";
import { useAuth } from "../context/AuthContext";

export default function Unauthorized() {
  const { user } = useAuth();

  return (
    <div className="center-page">
      <section className="panel login-card">
        <h1>Access unavailable</h1>
        <p>This page is not part of your current demo role.</p>

        <Link to={user ? `/${user.role}/overview` : "/login"}>
          Return to your dashboard
        </Link>
      </section>
    </div>
  );
}