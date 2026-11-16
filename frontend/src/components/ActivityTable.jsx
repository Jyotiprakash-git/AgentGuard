import { useState } from "react";
import { Link } from "react-router";

export default function ActivityTable({ events, investigate = false }) {
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("ALL");

  const filtered = events.filter((event) => {
    const matchesText = [
      event.id,
      event.tool,
      event.target,
      event.reason,
    ]
      .join(" ")
      .toLowerCase()
      .includes(search.toLowerCase());

    return (
      matchesText &&
      (filter === "ALL" || event.decision === filter)
    );
  });

  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Request activity</h2>

        <div className="filters">
          <input
            aria-label="Search activity"
            placeholder="Search requests..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            aria-label="Filter decisions"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          >
            <option value="ALL">All decisions</option>
            <option value="ALLOW">Allowed</option>
            <option value="BLOCK">Blocked</option>
            <option value="PENDING">Pending</option>
          </select>
        </div>
      </div>

      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Request</th>
              <th>Tool / Target</th>
              <th>Decision</th>
              <th>Reason</th>
              {investigate && <th>Action</th>}
            </tr>
          </thead>

          <tbody>
            {filtered.map((event) => (
              <tr key={event.id}>
                <td>{event.id}</td>
                <td>
                  <strong>{event.tool}</strong>
                  <small>{event.target}</small>
                </td>
                <td>
                  <span className={`badge ${event.decision.toLowerCase()}`}>
                    {event.decision}
                  </span>
                </td>
                <td>{event.reason}</td>

                {investigate && (
                  <td>
                    <Link to={`/analyst/investigations/${event.id}`}>
                      Investigate
                    </Link>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {!filtered.length && <p className="empty">No matching requests.</p>}
    </section>
  );
}