use std::{
    sync::atomic::{AtomicU64, Ordering},
    time::Duration,
};

use app_contracts::{PythonCallResult, PythonHostEnvelope, PythonHostRequest};
use serde::{Serialize, de::DeserializeOwned};
use tauri::{AppHandle, Runtime, async_runtime::Receiver};
use tauri_plugin_shell::{
    ShellExt,
    process::{CommandChild, CommandEvent},
};
use tokio::{sync::Mutex, time::timeout};

use crate::{PythonHostError, PythonWorker};

const HOST_BINARY_NAME: &str = "python-host";
const RESPONSE_TIMEOUT: Duration = Duration::from_secs(60);
static NEXT_REQUEST_ID: AtomicU64 = AtomicU64::new(1);

#[derive(Debug)]
pub struct PythonHostManager {
    process: Mutex<Option<PythonHostProcess>>,
}

impl Default for PythonHostManager {
    fn default() -> Self {
        Self {
            process: Mutex::new(None),
        }
    }
}

impl PythonHostManager {
    pub async fn execute<R, TRequest, TResponse>(
        &self,
        app: &AppHandle<R>,
        worker: PythonWorker,
        payload: &TRequest,
    ) -> Result<PythonCallResult<TResponse>, PythonHostError>
    where
        R: Runtime,
        TRequest: Serialize,
        TResponse: DeserializeOwned,
    {
        let request_id = next_request_id();
        let request = PythonHostRequest {
            request_id: request_id.clone(),
            worker: worker.name().to_owned(),
            payload,
        };
        let mut request_line = serde_json::to_vec(&request).map_err(PythonHostError::Serialize)?;
        request_line.push(b'\n');

        // The starter intentionally serializes calls through one host process.
        // This guarantees that one stdout line belongs to the request just written.
        let mut state = self.process.lock().await;
        if state.is_none() {
            *state = Some(PythonHostProcess::spawn(app)?);
        }

        let result = exchange(
            state.as_mut().expect("Python Host process must exist"),
            worker,
            &request_id,
            &request_line,
        )
        .await;

        if result
            .as_ref()
            .is_err_and(PythonHostError::invalidates_process)
            && let Some(process) = state.take()
        {
            process.kill();
        }

        result
    }
}

#[derive(Debug)]
struct PythonHostProcess {
    child: Option<CommandChild>,
    events: Receiver<CommandEvent>,
}

impl PythonHostProcess {
    fn spawn<R: Runtime>(app: &AppHandle<R>) -> Result<Self, PythonHostError> {
        let (events, child) = app
            .shell()
            .sidecar(HOST_BINARY_NAME)
            .map_err(|error| PythonHostError::Shell(error.to_string()))?
            .spawn()
            .map_err(|error| PythonHostError::Shell(error.to_string()))?;

        Ok(Self {
            child: Some(child),
            events,
        })
    }

    fn child_mut(&mut self) -> Result<&mut CommandChild, PythonHostError> {
        self.child
            .as_mut()
            .ok_or(PythonHostError::EventStreamClosed)
    }

    fn kill(mut self) {
        if let Some(child) = self.child.take() {
            let _ = child.kill();
        }
    }
}

impl Drop for PythonHostProcess {
    fn drop(&mut self) {
        if let Some(child) = self.child.take() {
            let _ = child.kill();
        }
    }
}

async fn exchange<TResponse>(
    process: &mut PythonHostProcess,
    worker: PythonWorker,
    request_id: &str,
    request_line: &[u8],
) -> Result<PythonCallResult<TResponse>, PythonHostError>
where
    TResponse: DeserializeOwned,
{
    process
        .child_mut()?
        .write(request_line)
        .map_err(|error| PythonHostError::Shell(error.to_string()))?;

    loop {
        let event = timeout(RESPONSE_TIMEOUT, process.events.recv())
            .await
            .map_err(|_| PythonHostError::Timeout {
                seconds: RESPONSE_TIMEOUT.as_secs(),
            })?
            .ok_or(PythonHostError::EventStreamClosed)?;

        match event {
            CommandEvent::Stdout(line) => {
                let envelope: PythonHostEnvelope<TResponse> =
                    serde_json::from_slice(&line).map_err(PythonHostError::Decode)?;
                validate_envelope(worker, request_id, &envelope)?;

                if let Some(error) = envelope.error {
                    return Err(PythonHostError::Worker {
                        code: error.code,
                        message: error.message,
                    });
                }

                let data = envelope.data.ok_or(PythonHostError::MissingData)?;
                return Ok(PythonCallResult {
                    data,
                    meta: envelope.meta,
                });
            }
            CommandEvent::Stderr(line) => {
                eprintln!("[python-host] {}", String::from_utf8_lossy(&line));
            }
            CommandEvent::Error(message) => {
                return Err(PythonHostError::Process(message));
            }
            CommandEvent::Terminated(payload) => {
                return Err(PythonHostError::Terminated {
                    code: payload.code,
                    signal: payload.signal,
                });
            }
            _ => {}
        }
    }
}

fn validate_envelope<T>(
    worker: PythonWorker,
    request_id: &str,
    envelope: &PythonHostEnvelope<T>,
) -> Result<(), PythonHostError> {
    if envelope.request_id.as_deref() != Some(request_id) {
        return Err(PythonHostError::RequestMismatch {
            expected: request_id.to_owned(),
            received: envelope.request_id.clone(),
        });
    }

    if envelope.meta.protocol_version != app_core::PROTOCOL_VERSION {
        return Err(PythonHostError::ProtocolMismatch {
            expected: app_core::PROTOCOL_VERSION,
            received: envelope.meta.protocol_version,
        });
    }

    if envelope.meta.host != HOST_BINARY_NAME {
        return Err(PythonHostError::HostMismatch {
            expected: HOST_BINARY_NAME.to_owned(),
            received: envelope.meta.host.clone(),
        });
    }

    if envelope.meta.worker != worker.name() {
        return Err(PythonHostError::WorkerMismatch {
            expected: worker.name().to_owned(),
            received: envelope.meta.worker.clone(),
        });
    }

    Ok(())
}

fn next_request_id() -> String {
    let sequence = NEXT_REQUEST_ID.fetch_add(1, Ordering::Relaxed);
    format!("rust-{}-{sequence}", std::process::id())
}
