import { useAuth } from "../../context/AuthContext";
import ActivityTable from "../../components/ActivityTable";

export default function Alerts() {
  const { events } = useAuth();

  return (
    <>
      <div className="page-title">
        <h1>Security alerts</h1>
        <p>Blocked requests requiring investigation.</p>
      </div>

      <ActivityTable
        events={events.filter((event) => event.decision === "BLOCK")}
        investigate
      />
    </>
  );
}