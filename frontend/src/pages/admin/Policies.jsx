import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Policies() {
  const { policy, savePolicy } = useAuth();

  const [documents, setDocuments] = useState(policy.documents.join(", "));
  const [recipients, setRecipients] = useState(policy.recipients.join(", "));
  const [requireApproval, setRequireApproval] = useState(
    policy.requireApproval
  );
  const [message, setMessage] = useState("");

  function parseList(value) {
    return [...new Set(
      value.split(",").map((item) => item.trim()).filter(Boolean)
    )];
  }

  function submit(event) {
    event.preventDefault();

    savePolicy({
      documents: parseList(documents),
      recipients: parseList(recipients),
      requireApproval,
    });

    setMessage("Policy saved. Existing pending approvals were invalidated.");
  }

  return (
    <>
      <div className="page-title">
        <h1>Security policies</h1>
        <p>Default-deny configuration · Version {policy.version}</p>
      </div>

      <form className="panel padded" onSubmit={submit}>
        <label>
          Permitted document IDs
          <input
            value={documents}
            onChange={(e) => setDocuments(e.target.value)}
          />
          <small>Separate IDs with commas.</small>
        </label>

        <label>
          Permitted email recipients
          <input
            value={recipients}
            onChange={(e) => setRecipients(e.target.value)}
          />
          <small>Separate exact addresses with commas.</small>
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={requireApproval}
            onChange={(e) => setRequireApproval(e.target.checked)}
          />
          Require approval for permitted emails
        </label>

        <p>Document deletion and unknown tools are always blocked.</p>

        <button className="primary" type="submit">Save policy</button>
        {message && <p role="status">{message}</p>}
      </form>
    </>
  );
}