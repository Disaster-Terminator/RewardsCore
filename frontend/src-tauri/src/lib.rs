use std::sync::atomic::{AtomicU16, Ordering};
use std::sync::Mutex;

use tauri::{AppHandle, Manager, Wry, Emitter};
use tauri_plugin_shell::process::CommandChild;
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{TrayIconBuilder, TrayIconEvent, MouseButton};

static BACKEND_PORT: AtomicU16 = AtomicU16::new(0);
static BACKEND_CHILD: Mutex<Option<CommandChild>> = Mutex::new(None);

const FALLBACK_PORT: u16 = 8000;

fn find_available_port() -> u16 {
    if let Some(port) = portpicker::pick_unused_port() {
        return port;
    }

    log::warn!("portpicker failed, using fallback port");
    FALLBACK_PORT
}

#[tauri::command]
fn get_backend_port() -> u16 {
    let port = BACKEND_PORT.load(Ordering::SeqCst);
    if port == 0 {
        FALLBACK_PORT
    } else {
        port
    }
}

#[tauri::command]
fn terminate_backend() -> Result<(), String> {
    if let Ok(mut guard) = BACKEND_CHILD.lock() {
        if let Some(child) = guard.take() {
            child.kill().map_err(|e| e.to_string())?;
            log::info!("Backend process terminated via command");
        }
    }
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![get_backend_port, terminate_backend])
        .setup(|app| {
            // Setup Tray Icon
            let quit_i = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let show_i = MenuItem::with_id(app, "show", "Show/Hide Window", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&show_i, &quit_i])?;

            let tray_builder = TrayIconBuilder::new()
                .menu(&menu)
                .on_menu_event(|app: &AppHandle, event| match event.id.as_ref() {
                    "quit" => {
                        log::info!("Quit from tray");
                        // Kill backend before exit
                        if let Ok(mut guard) = BACKEND_CHILD.lock() {
                            if let Some(child) = guard.take() {
                                let _ = child.kill();
                            }
                        }
                        app.exit(0);
                    }
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let is_visible = window.is_visible().unwrap_or(false);
                            if is_visible {
                                let _ = window.hide();
                            } else {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let is_visible = window.is_visible().unwrap_or(false);
                            if is_visible {
                                let _ = window.hide();
                            } else {
                                let _ = window.show();
                                let _ = window.set_focus();
                            }
                        }
                    }
                });

            // Set icon safely
            let tray = if let Some(icon) = app.default_window_icon() {
                tray_builder.icon(icon.clone()).build(app)?
            } else {
                tray_builder.build(app)?
            };

            if cfg!(debug_assertions) {
                let _ = app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                );
            }

            #[cfg(not(debug_assertions))]
            {
                use tauri_plugin_shell::ShellExt;
                use tauri_plugin_shell::process::CommandEvent;
                
                let port = find_available_port();
                BACKEND_PORT.store(port, Ordering::SeqCst);
                log::info!("Assigned dynamic port for backend: {}", port);

                let app_handle = app.handle().clone();
                let shell = app.shell();

                match shell.sidecar("backend") {
                    Ok(command) => {
                        match command.spawn() {
                            Ok((mut rx, child)) => {
                                if let Ok(mut guard) = BACKEND_CHILD.lock() {
                                    *guard = Some(child);
                                }

                                tauri::async_runtime::spawn(async move {
                                    while let Some(event) = rx.recv().await {
                                        match event {
                                            CommandEvent::Stdout(line) => {
                                                let log_line =
                                                    String::from_utf8_lossy(&line).to_string();
                                                log::info!("[Backend] {}", log_line.trim());
                                                let _ = app_handle.emit("py-log", log_line);
                                            }
                                            CommandEvent::Stderr(line) => {
                                                let log_line =
                                                    String::from_utf8_lossy(&line).to_string();
                                                log::error!(
                                                    "[Backend Error] {}",
                                                    log_line.trim()
                                                );
                                                let _ = app_handle.emit("py-error", log_line);
                                            }
                                            CommandEvent::Error(err) => {
                                                log::error!("[Backend Process Error] {}", err);
                                                let _ = app_handle.emit(
                                                    "py-error",
                                                    format!("Process error: {}", err),
                                                );
                                            }
                                            CommandEvent::Terminated(payload) => {
                                                log::info!(
                                                    "[Backend] Process terminated with code: {:?}",
                                                    payload.code
                                                );
                                                let _ = app_handle
                                                    .emit("backend-terminated", payload.code);
                                                if let Ok(mut guard) = BACKEND_CHILD.lock() {
                                                    *guard = None;
                                                }
                                            }
                                            _ => {}
                                        }
                                    }
                                });
                            }
                            Err(e) => {
                                log::error!("Failed to spawn backend sidecar: {}", e);
                            }
                        }
                    }
                    Err(e) => {
                        log::error!("Failed to create sidecar command: {}", e);
                    }
                }
            }

            #[cfg(debug_assertions)]
            {
                log::info!(
                    "Running in development mode. Using fixed port {} for backend.",
                    FALLBACK_PORT
                );
                log::info!("Make sure to start the Python backend manually: python web_server.py");
            }

            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                log::info!("Window close requested, hiding window instead of terminating...");
                api.prevent_close();
                let _ = window.hide();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
