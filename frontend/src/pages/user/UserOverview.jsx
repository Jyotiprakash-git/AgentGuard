import { useAuth } from "../../context/AuthContext";
import StatCard from "../../components/StatCard";
import ActivityTable from "../../components/ActivityTable";

export default function UserOverview() {
  const { user, events } = useAuth();
  const mine = events.filter((event) => event.userId === user.id);

  return (
    <>
      <div className="page-title">
        <h1>Welcome, {user.name}</h1>
        <p>Track your agent requests and their decisions.</p>
      </div>

      <div className="stats">
        <StatCard title="My requests" value={mine.length} />
        <StatCard
          title="Allowed"
          value={mine.filter((e) => e.decision === "ALLOW").length}
          tone="green"
        />
        <StatCard
          title="Blocked"
          value={mine.filter((e) => e.decision === "BLOCK").length}
          tone="red"
        />
        <StatCard
          title="Pending"
          value={mine.filter((e) => e.decision === "PENDING").length}
          tone="yellow"
        />
      </div>

      <ActivityTable events={mine.slice(0, 5)} />
    </>
  );
}