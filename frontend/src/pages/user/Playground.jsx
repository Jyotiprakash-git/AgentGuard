import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function Playground() {
  const { runRequest } = useAuth();
  const [tool, setTool] = useState("read_document");
  const [target, setTarget] = useState("public-meeting-report");
  const [result, setResult] = useState(null);

  function submit(event) {
    event.preventDefault();

    if (!target.trim()) return;

    setResult(runRequest(tool, target.trim()));
  }

  return (
    <>
      <div className="page-title">
        <h1>Agent playground</h1>
        <p>Submit a direct tool request to the policy simulator.</p>
      </div>

      <div className="two-columns">
        <form className="panel padded" onSubmit={submit}>
          <h2>New request</h2>

          <label>
            Tool
            <select value={tool} onChange={(e) => setTool(e.target.value)}>
              <option value="read_document">read_document</option>
              <option value="send_email">send_email</option>
              <option value="delete_document">delete_document</option>
            </select>
          </label>

          <label>
            {tool === "send_email" ? "Recipient" : "Document ID"}
            <input
              required
              value={target}
              onChange={(e) => setTarget(e.target.value)}
            />
          </label>

          <button className="primary" type="submit">Run request</button>

          <p className="hint">
            Try public-meeting-report, private-payroll, or
            manager@company.test with the appropriate tool.
          </p>
        </form>

        <section className="panel padded">
          <h2>Response</h2>

          {result ? (
            <>
              <span className={`badge ${result.decision.toLowerCase()}`}>
                {result.decision}
              </span>
              <p>{result.reason}</p>
              <pre>{JSON.stringify(result, null, 2)}</pre>
            </>
          ) : (
            <p className="empty">Run a request to see its result.</p>
          )}
        </section>
      </div>
    </>
  );
}