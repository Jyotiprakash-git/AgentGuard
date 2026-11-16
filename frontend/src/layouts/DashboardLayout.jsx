import { Outlet } from "react-router";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

export default function DashboardLayout() {
  return (
    <div className="dashboard">
      <Sidebar />

      <main className="main">
        <Header />

        <div className="content">

          <Outlet />
        </div>
      </main>
    </div>
  );
}