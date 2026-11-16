import { useAuth } from "../../context/AuthContext";

export default function Approvals() {
  const { events, decideApproval } = useAuth();
  const pending = events.filter((event) => event.decision === "PENDING");

  return (
    <>
      <div className="page-title">
        <h1>Approval queue</h1>
        <p>Review exact requests. New requests expire after 15 minutes.</p>
      </div>

      <section className="panel padded">
        {!pending.length && <p className="empty">No pending approvals.</p>}

        {pending.map((event) => (
          <div className="list-row" key={event.id}>
            <div>
              <h3>{event.tool}</h3>
              <p>{event.target}</p>
              <small>{event.id} · {event.time}</small>
            </div>

            <div className="button-group">
              <button onClick={() => decideApproval(event.id, false)}>
                Reject
              </button>
              <button
                className="primary"
                onClick={() => decideApproval(event.id, true)}
              >
                Approve
              </button>
            </div>
          </div>
        ))}
      </section>
    </>
  );
}