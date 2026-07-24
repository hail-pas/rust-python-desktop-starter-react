import { useState } from "react";
import type { ChangeEvent } from "react";
import type { DesktopApi } from "../../shared/api/desktop-api";
import type {
  PythonHostMeta,
  StatisticsResponse,
} from "../../shared/types/contracts";

interface StatisticsCardProps {
  api: DesktopApi;
  disabled: boolean;
  run<T>(operation: () => Promise<T>): Promise<T | undefined>;
}

function parseValues(source: string): number[] {
  return source.split(",").map((item, index) => {
    const value = Number(item.trim());
    if (!Number.isFinite(value)) {
      throw new Error(`第 ${index + 1} 个值不是有效数字`);
    }
    return value;
  });
}

export function StatisticsCard({
  api,
  disabled,
  run,
}: StatisticsCardProps) {
  const [values, setValues] = useState("1, 2, 3, 4, 5");
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [meta, setMeta] = useState<PythonHostMeta | null>(null);

  async function submit() {
    const result = await run(async () => {
      const parsed = parseValues(values);
      return api.statistics({ values: parsed });
    });
    if (result) {
      setStatistics(result.data);
      setMeta(result.meta);
    }
  }

  return (
    <article className="panel">
      <div>
        <p className="eyebrow">LOGICAL WORKER 02</p>
        <h2>Statistics</h2>
        <p>与 Greeter 共用同一个 Python Runtime 和 Host PID。</p>
      </div>
      <label>
        逗号分隔数字
        <input
          value={values}
          onChange={(event: ChangeEvent<HTMLInputElement>) =>
            setValues(event.target.value)
          }
        />
      </label>
      <button type="button" disabled={disabled} onClick={submit}>
        调用 Python Statistics
      </button>
      <output aria-live="polite">
        {statistics ? JSON.stringify(statistics, null, 2) : "等待调用"}
        {meta ? `

Host PID: ${meta.hostPid} · Worker: ${meta.worker}` : ""}
      </output>
    </article>
  );
}
