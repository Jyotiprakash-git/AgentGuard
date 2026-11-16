import { useAuth } from "../../context/AuthContext";
import { demoUsers } from "../../data/mockData";
import StatCard from "../../components/StatCard";
import ActivityTable from "../../components/ActivityTable";

export default function AdminOverview() {
  const { events, policy } = useAuth();

  return (
    <>
      <div className="page-title">
        <h1>Admin dashboard</h1>
        <p>Manage policy configuration and approval decisions.</p>
      </div>

      <div className="stats">
        <StatCard title="Demo accounts" value={demoUsers.length} />
        <StatCard title="Requests" value={events.length} />
        <StatCard
          title="Pending approvals"
          value={events.filter((event) => event.decision === "PENDING").length}
          tone="yellow"
        />
        <StatCard title="Policy version" value={`v${policy.version}`} />
      </div>

      <ActivityTable events={events} />
    </>
  );
}