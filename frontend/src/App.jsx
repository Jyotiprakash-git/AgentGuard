import { Navigate, Route, Routes } from "react-router";

import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./layouts/DashboardLayout";
import { useAuth } from "./context/AuthContext";

import Login from "./pages/Login";
import SignUp from "./pages/SignUp";
import Unauthorized from "./pages/Unauthorized";

import UserOverview from "./pages/user/UserOverview";
import Playground from "./pages/user/Playground";
import MyActivity from "./pages/user/MyActivity";
import MyApprovals from "./pages/user/MyApprovals";

import AnalystOverview from "./pages/analyst/AnalystOverview";
import ActivityMonitor from "./pages/analyst/ActivityMonitor";
import Alerts from "./pages/analyst/Alerts";
import Investigation from "./pages/analyst/Investigation";

import AdminOverview from "./pages/admin/AdminOverview";
import Users from "./pages/admin/Users";
import Policies from "./pages/admin/Policies";
import Approvals from "./pages/admin/Approvals";
import Agents from "./pages/admin/Agents";

function HomeRedirect() {
  const { user } = useAuth();

  return (
    <Navigate
      to={user ? `/${user.role}/overview` : "/login"}
      replace
    />
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="/unauthorized" element={<Unauthorized />} />

      <Route element={<ProtectedRoute allowedRoles={["user"]} />}>
        <Route path="/user" element={<DashboardLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<UserOverview />} />
          <Route path="playground" element={<Playground />} />
          <Route path="activity" element={<MyActivity />} />
          <Route path="approvals" element={<MyApprovals />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={["analyst"]} />}>
        <Route path="/analyst" element={<DashboardLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<AnalystOverview />} />
          <Route path="activity" element={<ActivityMonitor />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="investigations/:id" element={<Investigation />} />
        </Route>
      </Route>

      <Route element={<ProtectedRoute allowedRoles={["admin"]} />}>
        <Route path="/admin" element={<DashboardLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<AdminOverview />} />
          <Route path="users" element={<Users />} />
          <Route path="policies" element={<Policies />} />
          <Route path="approvals" element={<Approvals />} />
          <Route path="agents" element={<Agents />} />
        </Route>
      </Route>

      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  );
}