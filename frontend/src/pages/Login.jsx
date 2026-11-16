// import { useState } from "react";
// import { Link, Navigate, useNavigate } from "react-router";

// import {
//   Shield,
//   Mail,
//   LockKeyhole,
//   Eye,
//   EyeOff,
//   ArrowRight,
//   AlertCircle,
// } from "lucide-react";

// import { useAuth } from "../context/AuthContext";

// export default function Login() {
//   const { user, login } = useAuth();
//   const navigate = useNavigate();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [role, setRole] = useState("user");
//   const [showPassword, setShowPassword] = useState(false);
//   const [error, setError] = useState("");

//   if (user) {
//     return <Navigate to={`/${user.role}/overview`} replace />;
//   }

//   function handleSubmit(event) {
//     event.preventDefault();
//     setError("");

//     try {
//       const account = login(email, password, role);

//       navigate(`/${account.role}/overview`, {
//         replace: true,
//       });
//     } catch (err) {
//       setError(err.message || "Unable to continue.");
//     }
//   }

//   return (
//     <div className="auth-page">
//       <section className="auth-intro">
//         <Link to="/" className="auth-brand">
//           <span className="auth-brand-icon">
//             <Shield size={28} />
//           </span>

//           <span>
//             AgentGuard <strong>OS</strong>
//           </span>
//         </Link>

//         <div className="auth-intro-content">
//           <span className="auth-eyebrow">
//             AI AGENT SECURITY PLATFORM
//           </span>

//           <h1>
//             Powerful agents.
//             <br />
//             Clear boundaries.
//           </h1>

//           <p className="auth-intro-description">
//             Monitor activity, manage policies, and review
//             sensitive actions from one workspace.
//           </p>
//         </div>

//         <p className="auth-intro-footer">
//           AgentGuard OS · AI security workspace
//         </p>
//       </section>

//       <main className="auth-form-side">
//         <section className="auth-card">
//           <div className="auth-heading">
//             <span className="auth-heading-icon">
//               <LockKeyhole size={24} />
//             </span>

//             <h2>Welcome back</h2>
//             <p>Sign in to your workspace.</p>
//           </div>

//           <form onSubmit={handleSubmit}>
//             <label className="auth-label" htmlFor="login-email">
//               Email address
//             </label>

//             <div className="auth-input-wrap">
//               <Mail size={19} aria-hidden="true" />

//               <input
//                 id="login-email"
//                 type="email"
//                 autoComplete="username"
//                 placeholder="you@company.com"
//                 value={email}
//                 onChange={(event) => setEmail(event.target.value)}
//                 required
//               />
//             </div>

//             <label className="auth-label" htmlFor="login-password">
//               Password
//             </label>

//             <div className="auth-input-wrap">
//               <LockKeyhole size={19} aria-hidden="true" />

//               <input
//                 id="login-password"
//                 type={showPassword ? "text" : "password"}
//                 autoComplete="current-password"
//                 placeholder="Enter your password"
//                 value={password}
//                 onChange={(event) => setPassword(event.target.value)}
//                 required
//               />

//               <button
//                 type="button"
//                 className="auth-password-toggle"
//                 onClick={() => setShowPassword((current) => !current)}
//                 aria-label={showPassword ? "Hide password" : "Show password"}
//               >
//                 {showPassword ? <EyeOff size={19} /> : <Eye size={19} />}
//               </button>
//             </div>

//             <label className="auth-label" htmlFor="login-role">
//               Workspace
//             </label>

//             <select
//               id="login-role"
//               className="auth-role-select"
//               value={role}
//               onChange={(event) => setRole(event.target.value)}
//             >
//               <option value="user">User</option>
//               <option value="analyst">Analyst</option>
//               <option value="admin">Admin</option>
//             </select>

//             {error && (
//               <div className="auth-error" role="alert">
//                 <AlertCircle size={18} />
//                 <span>{error}</span>
//               </div>
//             )}

//             <button type="submit" className="auth-submit">
//               Sign in
//               <ArrowRight size={19} />
//             </button>

//             <p className="auth-switch">
//               New to AgentGuard?{" "}
//               <Link to="/signup">Create an account</Link>
//             </p>
//           </form>
//         </section>
//       </main>
//     </div>
//   );
// }
import { Navigate, useNavigate } from "react-router";
import {
  Shield,
  UserRound,
  ScanSearch,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";

const accounts = [
  {
    role: "user",
    name: "User",
    email: "user@agentguard.test",
    icon: UserRound,
    description: "Submit agent requests and track your activity.",
  },
  {
    role: "analyst",
    name: "Analyst",
    email: "analyst@agentguard.test",
    icon: ScanSearch,
    description: "Monitor security events and investigate alerts.",
  },
  {
    role: "admin",
    name: "Admin",
    email: "admin@agentguard.test",
    icon: ShieldCheck,
    description: "Manage policies, approvals, and workspace users.",
  },
];

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  if (user) {
    return <Navigate to={`/${user.role}/overview`} replace />;
  }

  function enterWorkspace(account) {
    // Uses your current frontend-only login function.
    const selectedUser = login(
      account.email,
      "local-preview",
      account.role
    );

    navigate(`/${selectedUser.role}/overview`, {
      replace: true,
    });
  }

  return (
    <main className="workspace-entry">
      <section className="workspace-entry-card">
        <div className="entry-brand">
          <Shield size={38} />
          <span>AgentGuard OS</span>
        </div>

        <h1>Choose your workspace</h1>

        <p className="entry-description">
          Select a role to open its dashboard.
        </p>

        <div className="entry-role-grid">
          {accounts.map((account) => {
            const Icon = account.icon;

            return (
              <button
                key={account.role}
                type="button"
                className="entry-role-card"
                onClick={() => enterWorkspace(account)}
              >
                <span className="entry-role-icon">
                  <Icon size={28} />
                </span>

                <strong>{account.name}</strong>

                <span className="entry-role-description">
                  {account.description}
                </span>

                <span className="entry-role-action">
                  Open dashboard
                  <ArrowRight size={17} />
                </span>
              </button>
            );
          })}
        </div>
      </section>
    </main>
  );
}