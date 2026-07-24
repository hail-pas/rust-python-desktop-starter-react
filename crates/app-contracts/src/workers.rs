use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GreeterRequest {
    pub name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct GreeterResponse {
    pub greeting: String,
    pub normalized_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct StatisticsRequest {
    pub values: Vec<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct StatisticsResponse {
    pub count: usize,
    pub sum: f64,
    pub mean: Option<f64>,
    pub minimum: Option<f64>,
    pub maximum: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonHostRequest<T> {
    pub request_id: String,
    pub worker: String,
    pub payload: T,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonHostMeta {
    pub host: String,
    pub host_pid: u32,
    pub host_started_at_unix_ms: u64,
    pub python_version: String,
    pub protocol_version: u32,
    pub worker: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonHostErrorPayload {
    pub code: String,
    pub message: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonHostEnvelope<T> {
    pub request_id: Option<String>,
    pub ok: bool,
    pub data: Option<T>,
    pub error: Option<PythonHostErrorPayload>,
    pub meta: PythonHostMeta,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PythonCallResult<T> {
    pub data: T,
    pub meta: PythonHostMeta,
}
