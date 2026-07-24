import { useState } from "react";
import type { ChangeEvent } from "react";
import type { DesktopApi } from "../../shared/api/desktop-api";
import type { PythonHostMeta } from "../../shared/types/contracts";

interface GreeterCardProps {
  api: DesktopApi;
  disabled: boolean;
  run<T>(operation: () => Promise<T>): Promise<T | undefined>;
}

export function GreeterCard({ api, disabled, run }: GreeterCardProps) {
  const [name, setName] = useState("Alice");
  const [greeting, setGreeting] = useState("");
  const [meta, setMeta] = useState<PythonHostMeta | null>(null);

  async function submit() {
    const result = await run(() => api.greet({ name }));
    if (result) {
      setGreeting(result.data.greeting);
      setMeta(result.meta);
    }
  }

  return (
    <article className="panel">
      <div>
        <p className="eyebrow">LOGICAL WORKER 01</p>
        <h2>Greeter</h2>
        <p>由同一个常驻 Python Host 分发的字符串处理逻辑 Worker。</p>
      </div>
      <label>
        姓名
        <input
          value={name}
          onChange={(event: ChangeEvent<HTMLInputElement>) =>
            setName(event.target.value)
          }
        />
      </label>
      <button type="button" disabled={disabled} onClick={submit}>
        调用 Python Greeter
      </button>
      <output aria-live="polite">
        {greeting || "等待调用"}
        {meta ? `

Host PID: ${meta.hostPid} · Worker: ${meta.worker}` : ""}
      </output>
    </article>
  );
}
