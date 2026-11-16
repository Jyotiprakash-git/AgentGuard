import { useAuth } from "../../context/AuthContext";

export default function MyApprovals() {
  const { user, events } = useAuth();

  const pending = events.filter(
    (event) =>
      event.userId === user.id && event.decision === "PENDING"
  );

  return (
    <>
      <div className="page-title">
        <h1>My approvals</h1>
        <p>Requests currently waiting for an administrator.</p>
      </div>

      <section className="panel padded">
        {!pending.length && <p className="empty">No pending requests.</p>}

        {pending.map((event) => (
          <div className="list-row" key={event.id}>
            <div>
              <h3>{event.tool}</h3>
              <p>{event.target}</p>
              <small>{event.id}</small>
            </div>
            <span className="badge pending">Waiting for review</span>
          </div>
        ))}
      </section>
    </>
  );
}