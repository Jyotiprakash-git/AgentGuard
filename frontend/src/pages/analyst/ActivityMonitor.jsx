import { useAuth } from "../../context/AuthContext";
import ActivityTable from "../../components/ActivityTable";

export default function ActivityMonitor() {
  const { events } = useAuth();

  return (
    <>
      <div className="page-title">
        <h1>Activity monitor</h1>
        <p>Inspect all requests in the demo workspace.</p>
      </div>

      <ActivityTable events={events} investigate />
    </>
  );
}