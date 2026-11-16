import { useAuth } from "../../context/AuthContext";
import ActivityTable from "../../components/ActivityTable";

export default function MyActivity() {
  const { user, events } = useAuth();

  return (
    <>
      <div className="page-title">
        <h1>My activity</h1>
        <p>Requests submitted by your demo account.</p>
      </div>

      <ActivityTable
        events={events.filter((event) => event.userId === user.id)}
      />
    </>
  );
}