import { useState } from "react";
import { Link, useParams } from "react-router";
import { useAuth } from "../../context/AuthContext";

function InvestigationForm({ event, onSave }) {
  const [note, setNote] = useState(event.note);
  const [saved, setSaved] = useState(false);

  function submit(e) {
    e.preventDefault();
    onSave(event.id, note);
    setSaved(true);
  }

  return (
    <form className="panel padded" onSubmit={submit}>
      <h2>{event.tool}</h2>
      <p>{event.reason}</p>

      <pre>
        {JSON.stringify(
          {
            id: event.id,
            target: event.target,
            decision: event.decision,
            time: event.time,
          },
          null,
          2
        )}
      </pre>

      <label>
        Investigation note
        <textarea
          value={note}
          onChange={(e) => {
            setNote(e.target.value);
            setSaved(false);
          }}
          placeholder="Record your findings..."
        />
      </label>

      <button className="primary" type="submit">Save note</button>
      {saved && <p role="status">Investigation note saved.</p>}

      <p className="hint">
        Investigation notes do not approve or execute a request.
      </p>
    </form>
  );
}

export default function Investigation() {
  const { id } = useParams();
  const { events, saveNote } = useAuth();
  const event = events.find((item) => item.id === id);

  if (!event) {
    return (
      <section className="panel padded">
        <h1>Request not found</h1>
        <Link to="/analyst/activity">Return to activity</Link>
      </section>
    );
  }

  return (
    <>
      <div className="page-title">
        <h1>Investigate request</h1>
        <p>{event.id}</p>
      </div>

      <InvestigationForm key={event.id} event={event} onSave={saveNote} />
    </>
  );
}