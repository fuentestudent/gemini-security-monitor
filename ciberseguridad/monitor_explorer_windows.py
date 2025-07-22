import pygetwindow as gw
import json
import datetime

LOG_FILE = "C:\\www\\ciberseguridad\\explorer_window_log.txt"
STATE_FILE = "C:\\www\\ciberseguridad\\explorer_window_state.json"

def get_explorer_windows():
    windows_data = []
    try:
        for window in gw.getWindowsWithTitle('Explorador de archivos'):
            windows_data.append({
                "title": window.title,
                "left": window.left,
                "top": window.top,
                "width": window.width,
                "height": window.height,
                "process_id": window._hWnd  # Using internal handle as a pseudo-PID for now
            })
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{datetime.datetime.now()} - ERROR al obtener ventanas: {e}\n")
    return windows_data

def load_previous_state():
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_current_state(current_windows):
    with open(STATE_FILE, "w") as f:
        json.dump(current_windows, f, indent=4)

def monitor_explorer_windows():
    current_windows = get_explorer_windows()
    previous_windows = load_previous_state()

    log_entries = []
    changes_detected = False

    # Check for changes in existing windows
    for current_win in current_windows:
        match = next((pw for pw in previous_windows if pw['title'] == current_win['title'] and pw['process_id'] == current_win['process_id']), None)
        if match:
            if (match['left'] != current_win['left'] or \
                match['top'] != current_win['top'] or \
                match['width'] != current_win['width'] or \
                match['height'] != current_win['height']):
                
                log_entries.append(f"{datetime.datetime.now()} - CAMBIO DETECTADO: Ventana '{current_win['title']}' (PID: {current_win['process_id']}) - Tamaño/Posición anterior: (Left: {match['left']}, Top: {match['top']}, Width: {match['width']}, Height: {match['height']}) - Nuevo: (Left: {current_win['left']}, Top: {current_win['top']}, Width: {current_win['width']}, Height: {current_win['height']})")
                changes_detected = True
        else:
            # New window detected
            log_entries.append(f"{datetime.datetime.now()} - NUEVA VENTANA: Ventana '{current_win['title']}' (PID: {current_win['process_id']}) - Tamaño/Posición: (Left: {current_win['left']}, Top: {current_win['top']}, Width: {current_win['width']}, Height: {current_win['height']})")
            changes_detected = True

    # Check for closed windows
    for previous_win in previous_windows:
        match = next((cw for cw in current_windows if cw['title'] == previous_win['title'] and cw['process_id'] == previous_win['process_id']), None)
        if not match:
            log_entries.append(f"{datetime.datetime.now()} - VENTANA CERRADA: Ventana '{previous_win['title']}' (PID: {previous_win['process_id']})")
            changes_detected = True

    if log_entries:
        with open(LOG_FILE, "a") as f:
            for entry in log_entries:
                f.write(entry + "\n")

    save_current_state(current_windows)

if __name__ == "__main__":
    monitor_explorer_windows()