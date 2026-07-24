export interface HealthResponse {
  application: string;
  rustCore: string;
  protocolVersion: number;
}

export interface GreeterRequest {
  name: string;
}

export interface GreeterResponse {
  greeting: string;
  normalizedName: string;
}

export interface StatisticsRequest {
  values: number[];
}

export interface StatisticsResponse {
  count: number;
  sum: number;
  mean: number | null;
  minimum: number | null;
  maximum: number | null;
}

export interface PythonHostMeta {
  host: string;
  hostPid: number;
  hostStartedAtUnixMs: number;
  pythonVersion: string;
  protocolVersion: number;
  worker: string;
}

export interface PythonCallResult<T> {
  data: T;
  meta: PythonHostMeta;
}
