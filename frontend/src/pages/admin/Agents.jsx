export default function Agents() {
  const tools = [
    ["read_document", "Read permitted synthetic documents", "Available"],
    ["send_email", "Simulate email after policy checks", "Available"],
    ["delete_document", "Destructive document operation", "Blocked"],
  ];

  return (
    <>
      <div className="page-title">
        <h1>Agents & tools</h1>
        <p>demo-assistant · Direct tool-call simulator</p>
      </div>

      <section className="panel padded">
        <p>No LLM or external tool service is connected.</p>

        {tools.map(([name, description, status]) => (
          <div className="list-row" key={name}>
            <div>
              <h3>{name}</h3>
              <p>{description}</p>
            </div>

            <span className={`badge ${status === "Blocked" ? "block" : "allow"}`}>
              {status}
            </span>
          </div>
        ))}
      </section>
    </>
  );
}