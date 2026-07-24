use thiserror::Error;

#[derive(Debug, Error)]
pub enum PythonHostError {
    #[error("failed to serialize a Python Host request: {0}")]
    Serialize(serde_json::Error),

    #[error("failed to decode a Python Host response: {0}")]
    Decode(serde_json::Error),

    #[error("failed to create, start, or communicate with the Python Host: {0}")]
    Shell(String),

    #[error("Python Host response timed out after {seconds} seconds")]
    Timeout { seconds: u64 },

    #[error("Python Host event stream closed unexpectedly")]
    EventStreamClosed,

    #[error("Python Host process terminated: code={code:?}, signal={signal:?}")]
    Terminated {
        code: Option<i32>,
        signal: Option<i32>,
    },

    #[error("Python Host process error: {0}")]
    Process(String),

    #[error("Python Host protocol mismatch: expected {expected}, received {received}")]
    ProtocolMismatch { expected: u32, received: u32 },

    #[error("unexpected Python Host identity: expected {expected}, received {received}")]
    HostMismatch { expected: String, received: String },

    #[error("unexpected logical worker identity: expected {expected}, received {received}")]
    WorkerMismatch { expected: String, received: String },

    #[error("unexpected request id: expected {expected}, received {received:?}")]
    RequestMismatch {
        expected: String,
        received: Option<String>,
    },

    #[error("Python logical worker rejected request [{code}]: {message}")]
    Worker { code: String, message: String },

    #[error("Python Host returned no data")]
    MissingData,
}

impl PythonHostError {
    pub(crate) const fn invalidates_process(&self) -> bool {
        !matches!(self, Self::Serialize(_) | Self::Worker { .. })
    }
}
