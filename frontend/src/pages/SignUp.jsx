import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router";

import {
  Shield,
  UserRound,
  Mail,
  LockKeyhole,
  Eye,
  EyeOff,
  ArrowRight,
  AlertCircle,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

export default function SignUp() {
  const { user, signup } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");

  if (user) {
    return <Navigate to={`/${user.role}/overview`} replace />;
  }

  function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!name.trim()) {
      setError("Please enter your full name.");
      return;
    }

    if (password !== confirmPassword) {
      setError("The passwords do not match.");
      return;
    }

    try {
      const account = signup(name, email, password);

      navigate(`/${account.role}/overview`, {
        replace: true,
      });
    } catch (err) {
      setError(err.message || "Unable to continue.");
    }
  }

  return (
    <div className="auth-page">
      <section className="auth-intro">
        <Link to="/" className="auth-brand">
          <span className="auth-brand-icon">
            <Shield size={28} />
          </span>

          <span>
            AgentGuard <strong>OS</strong>
          </span>
        </Link>

        <div className="auth-intro-content">
          <span className="auth-eyebrow">
            AI AGENT SECURITY PLATFORM
          </span>

          <h1>
            Your workspace.
            <br />
            Your control.
          </h1>

          <p className="auth-intro-description">
            Access your dashboard to submit agent requests
            and track their results.
          </p>
        </div>

        <p className="auth-intro-footer">
          AgentGuard OS · AI security workspace
        </p>
      </section>

      <main className="auth-form-side">
        <section className="auth-card">
          <div className="auth-heading">
            <span className="auth-heading-icon">
              <UserRound size={24} />
            </span>

            <h2>Create your account</h2>
            <p>Enter your details to get started.</p>
          </div>

          <form onSubmit={handleSubmit}>
            <label className="auth-label" htmlFor="signup-name">
              Full name
            </label>

            <div className="auth-input-wrap">
              <UserRound size={19} aria-hidden="true" />

              <input
                id="signup-name"
                type="text"
                autoComplete="name"
                placeholder="Your full name"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
              />
            </div>

            <label className="auth-label" htmlFor="signup-email">
              Email address
            </label>

            <div className="auth-input-wrap">
              <Mail size={19} aria-hidden="true" />

              <input
                id="signup-email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
              />
            </div>

            <label className="auth-label" htmlFor="signup-password">
              Password
            </label>

            <div className="auth-input-wrap">
              <LockKeyhole size={19} aria-hidden="true" />

              <input
                id="signup-password"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Enter a password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />

              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword((current) => !current)}
                aria-label={showPassword ? "Hide passwords" : "Show passwords"}
              >
                {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
              </button>
            </div>

            <label className="auth-label" htmlFor="signup-confirm">
              Confirm password
            </label>

            <div className="auth-input-wrap">
              <LockKeyhole size={19} aria-hidden="true" />

              <input
                id="signup-confirm"
                type={showPassword ? "text" : "password"}
                autoComplete="new-password"
                placeholder="Enter your password again"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            </div>

            {error && (
              <div className="auth-error" role="alert">
                <AlertCircle size={18} />
                <span>{error}</span>
              </div>
            )}

            <button type="submit" className="auth-submit">
              Create account
              <ArrowRight size={19} />
            </button>

            <p className="auth-switch">
              Already have an account? <Link to="/login">Sign in</Link>
            </p>
          </form>
        </section>
      </main>
    </div>
  );
}