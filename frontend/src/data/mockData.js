export const demoUsers = [
  {
    id: "u1",
    name: "Alex Morgan",
    email: "user@agentguard.test",
    role: "user",
  },
  {
    id: "u2",
    name: "Sam Rivera",
    email: "analyst@agentguard.test",
    role: "analyst",
  },
  {
    id: "u3",
    name: "Jordan Lee",
    email: "admin@agentguard.test",
    role: "admin",
  },
];

export const initialPolicy = {
  version: 1,
  documents: ["public-meeting-report", "public-project-guide"],
  recipients: ["manager@company.test", "team@company.test"],
  requireApproval: true,
};

export const initialEvents = [
  {
    id: "AG-1001",
    userId: "u1",
    tool: "read_document",
    target: "public-meeting-report",
    decision: "ALLOW",
    reason: "Synthetic document read successfully.",
    time: "Demo fixture",
    note: "",
  },
  {
    id: "AG-1002",
    userId: "u1",
    tool: "send_email",
    target: "external@outside.test",
    decision: "BLOCK",
    reason: "Recipient is not permitted.",
    time: "Demo fixture",
    note: "",
  },
];