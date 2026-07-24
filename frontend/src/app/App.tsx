import { useEffect, useState } from "react";
import { GreeterCard } from "../features/greeter/GreeterCard";
import { StatisticsCard } from "../features/statistics/StatisticsCard";
import { desktopApi } from "../shared/api/desktop-api";
import { StatusCard } from "../shared/components/StatusCard";
import type { HealthResponse } from "../shared/types/contracts";

export function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState("");
  const [busyCount, setBusyCount] = useState(0);

  useEffect(() => {
    desktopApi.health().then(setHealth).catch((reason: unknown) => {
      setError(toMessage(reason));
    });
  }, []);

  async function run<T>(operation: () => Promise<T>): Promise<T | undefined> {
    setBusyCount((count) => count + 1);
    setError("");
    try {
      return await operation();
    } catch (reason) {
      setError(toMessage(reason));
      return undefined;
    } finally {
      setBusyCount((count) => Math.max(0, count - 1));
    }
  }

  const busy = busyCount > 0;

  return (
    <main className="layout">
      <header>
        <p className="eyebrow">LOCAL DESKTOP STARTER</p>
        <h1>Rust 主控，一个 Python Host，多逻辑 Worker</h1>
        <p className="subtitle">
          React → Tauri command → Rust PythonHostManager → 常驻 Python Host
        </p>
      </header>

      <section className="status-grid" aria-label="应用状态">
        <StatusCard label="Rust core" value={health?.rustCore ?? "loading"} />
        <StatusCard
          label="Protocol"
          value={health?.protocolVersion ?? "-"}
        />
        <StatusCard label="Python Host" value="persistent" />
      </section>

      <section className="worker-grid">
        <GreeterCard api={desktopApi} disabled={busy} run={run} />
        <StatisticsCard api={desktopApi} disabled={busy} run={run} />
      </section>

      {error && (
        <aside className="error" role="alert">
          {error}
        </aside>
      )}
    </main>
  );
}

function toMessage(reason: unknown): string {
  return reason instanceof Error ? reason.message : String(reason);
}
