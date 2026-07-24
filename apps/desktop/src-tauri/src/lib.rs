mod commands;

use python_host::PythonHostManager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(PythonHostManager::default())
        .invoke_handler(tauri::generate_handler![
            commands::health,
            commands::call_greeter,
            commands::call_statistics,
        ])
        .run(tauri::generate_context!())
        .expect("failed to run desktop application");
}
