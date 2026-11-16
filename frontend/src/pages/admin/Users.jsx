import { demoUsers } from "../../data/mockData";

export default function Users() {
  return (
    <>
      <div className="page-title">
        <h1>Users & roles</h1>
        <p>Sample directory. Account creation and editing require the backend.</p>
      </div>

      <section className="panel table-scroll">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody>
            {demoUsers.map((user) => (
              <tr key={user.id}>
                <td>{user.name}</td>
                <td>{user.email}</td>
                <td>{user.role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}