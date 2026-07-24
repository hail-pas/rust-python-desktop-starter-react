use app_contracts::{
    GreeterRequest, GreeterResponse, HealthResponse, PythonCallResult, StatisticsRequest,
    StatisticsResponse,
};
use python_host::{PythonHostManager, PythonWorker};
use tauri::{AppHandle, State};

#[tauri::command]
pub fn health() -> HealthResponse {
    app_core::health()
}

#[tauri::command]
pub async fn call_greeter(
    app: AppHandle,
    manager: State<'_, PythonHostManager>,
    request: GreeterRequest,
) -> Result<PythonCallResult<GreeterResponse>, String> {
    manager
        .execute(&app, PythonWorker::Greeter, &request)
        .await
        .map_err(|error| error.to_string())
}

#[tauri::command]
pub async fn call_statistics(
    app: AppHandle,
    manager: State<'_, PythonHostManager>,
    request: StatisticsRequest,
) -> Result<PythonCallResult<StatisticsResponse>, String> {
    manager
        .execute(&app, PythonWorker::Statistics, &request)
        .await
        .map_err(|error| error.to_string())
}
