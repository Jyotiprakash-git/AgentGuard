import { createContext, useContext, useState } from "react";

import {
  initialEvents,
  initialPolicy,
} from "../data/mockData";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [events, setEvents] = useState(initialEvents);
  const [policy, setPolicy] = useState(initialPolicy);

  // Frontend-only sign in.
  function login(email, password, role = "user") {
    if (!email.trim() || !password) {
      throw new Error("Please enter your email and password.");
    }

    if (!["user", "analyst", "admin"].includes(role)) {
      throw new Error("Invalid account role.");
    }

    const account = {
      id:
        role === "user"
          ? "u1"
          : role === "analyst"
            ? "u2"
            : "u3",
      name: email.trim().split("@")[0],
      email: email.trim(),
      role,
    };

    setUser(account);

    return account;
  }

  // Frontend-only sign up.
  function signup(name, email, password) {
    if (!name.trim() || !email.trim() || !password) {
      throw new Error("Please complete all fields.");
    }

    const account = {
      id: "u1",
      name: name.trim(),
      email: email.trim(),
      role: "user",
    };

    setUser(account);

    return account;
  }

  function logout() {
    setUser(null);
  }

  function runRequest(tool, target) {
    if (user?.role !== "user") {
      throw new Error("Sign in as a User to submit requests.");
    }

    let decision = "BLOCK";
    let reason = "Tool is not permitted.";

    if (tool === "read_document") {
      const allowed = policy.documents.includes(target);

      decision = allowed ? "ALLOW" : "BLOCK";
      reason = allowed
        ? "Synthetic document read successfully."
        : "Document is not permitted.";
    }

    if (tool === "send_email") {
      if (!policy.recipients.includes(target)) {
        reason = "Recipient is not permitted.";
      } else {
        decision = policy.requireApproval ? "PENDING" : "ALLOW";

        reason = policy.requireApproval
          ? "Administrator approval required."
          : "Simulated email completed. No real email was sent.";
      }
    }

    const request = {
      id: `AG-${crypto.randomUUID().slice(0, 8)}`,
      userId: user.id,
      tool,
      target,
      decision,
      reason,
      time: new Date().toLocaleString(),
      createdAt: Date.now(),
      policyVersion: policy.version,
      note: "",
    };

    setEvents((current) => [request, ...current]);

    return request;
  }

  function decideApproval(id, approved) {
    if (user?.role !== "admin") return;

    setEvents((current) =>
      current.map((event) => {
        if (event.id !== id || event.decision !== "PENDING") {
          return event;
        }

        const valid =
          event.policyVersion === policy.version &&
          Date.now() - event.createdAt < 15 * 60 * 1000 &&
          policy.recipients.includes(event.target);

        const allowed = approved && valid;

        return {
          ...event,
          decision: allowed ? "ALLOW" : "BLOCK",
          reason: allowed
            ? "Admin approved. Simulated email completed."
            : approved
              ? "Request expired or policy no longer permits it."
              : "Rejected by Admin.",
        };
      })
    );
  }

  function savePolicy(nextPolicy) {
    if (user?.role !== "admin") return;

    setPolicy((current) => ({
      ...nextPolicy,
      version: current.version + 1,
    }));

    setEvents((current) =>
      current.map((event) =>
        event.decision === "PENDING"
          ? {
              ...event,
              decision: "BLOCK",
              reason: "Policy changed. Submit a new request.",
            }
          : event
      )
    );
  }

  function saveNote(id, note) {
    if (user?.role !== "analyst") return;

    setEvents((current) =>
      current.map((event) =>
        event.id === id ? { ...event, note } : event
      )
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        events,
        policy,
        login,
        signup,
        logout,
        runRequest,
        decideApproval,
        savePolicy,
        saveNote,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }

  return context;
}