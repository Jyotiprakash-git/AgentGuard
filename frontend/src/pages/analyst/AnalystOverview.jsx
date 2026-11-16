import { useAuth } from "../../context/AuthContext";
import StatCard from "../../components/StatCard";
import ActivityTable from "../../components/ActivityTable";

export default function AnalystOverview() {
  const { events } = useAuth();
  const blocked = events.filter((event) => event.decision === "BLOCK");

  return (
    <>
      <div className="page-title">
        <h1>Security overview</h1>
        <p>Monitor blocked actions and record investigation findings.</p>
      </div>

      <div className="stats">
        <StatCard title="Total requests" value={events.length} />
        <StatCard title="Blocked requests" value={blocked.length} tone="red" />
        <StatCard
          title="Events with notes"
          value={events.filter((event) => event.note.trim()).length}
        />
      </div>

      <ActivityTable events={blocked} investigate />
    </>
  );
}