interface StatusCardProps {
  label: string;
  value: string | number;
}

export function StatusCard({ label, value }: StatusCardProps) {
  return (
    <article className="status-card">
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
