import { invoke } from "@tauri-apps/api/core";
import type {
  GreeterRequest,
  GreeterResponse,
  HealthResponse,
  PythonCallResult,
  StatisticsRequest,
  StatisticsResponse,
} from "../types/contracts";

export interface DesktopApi {
  health(): Promise<HealthResponse>;
  greet(request: GreeterRequest): Promise<PythonCallResult<GreeterResponse>>;
  statistics(
    request: StatisticsRequest,
  ): Promise<PythonCallResult<StatisticsResponse>>;
}

const tauriDesktopApi: DesktopApi = {
  health: () => invoke<HealthResponse>("health"),
  greet: (request) =>
    invoke<PythonCallResult<GreeterResponse>>("call_greeter", { request }),
  statistics: (request) =>
    invoke<PythonCallResult<StatisticsResponse>>("call_statistics", { request }),
};

const MOCK_META = {
  host: "python-host-mock",
  hostPid: 4242,
  hostStartedAtUnixMs: Date.now(),
  pythonVersion: "browser-mock",
  protocolVersion: 1,
};

const mockDesktopApi: DesktopApi = {
  async health() {
    return {
      application: "rust-python-desktop-starter (browser mock)",
      rustCore: "mock",
      protocolVersion: 1,
    };
  },
  async greet({ name }) {
    const normalizedName = name.trim().replace(/\s+/g, " ");
    if (!normalizedName) throw new Error("name must not be empty");
    return {
      data: {
        greeting: `你好，${normalizedName}！这是 React 浏览器预览的 mock 响应。`,
        normalizedName,
      },
      meta: { ...MOCK_META, worker: "greeter" },
    };
  },
  async statistics({ values }) {
    const sum = values.reduce((total, value) => total + value, 0);
    return {
      data: {
        count: values.length,
        sum,
        mean: values.length ? sum / values.length : null,
        minimum: values.length ? Math.min(...values) : null,
        maximum: values.length ? Math.max(...values) : null,
      },
      meta: { ...MOCK_META, worker: "statistics" },
    };
  },
};

export const desktopApi: DesktopApi =
  import.meta.env.VITE_USE_MOCKS === "1" ? mockDesktopApi : tauriDesktopApi;
