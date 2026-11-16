export default function StatCard({ title, value, tone = "" }) {
  return (
    <article className={`stat-card ${tone}`}>
      <p>{title}</p>
      <h2>{value}</h2>
    </article>
  );
}