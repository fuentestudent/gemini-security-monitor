import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import threading
import os

class SecurityMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Security Monitor")
        self.root.geometry("1000x700") # Aumentar el tamaño para más pestañas

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Pestaña "Estado General" ---
        self.general_status_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_status_frame, text="Estado General")
        self.create_general_status_tab(self.general_status_frame)

        # --- Pestaña "Logs de Seguridad" ---
        self.security_logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.security_logs_frame, text="Logs de Seguridad")
        self.create_security_logs_tab(self.security_logs_frame)

        # --- Pestaña "Integridad de C:\www" ---
        self.integrity_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.integrity_frame, text="Integridad de C:\www")
        self.create_integrity_tab(self.integrity_frame)

        # --- Pestaña "Configuración/Acerca de" ---
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="Configuración/Acerca de")
        self.create_about_tab(self.about_frame)

    def create_general_status_tab(self, parent_frame):
        # Botón para ejecutar el script maestro
        run_button = ttk.Button(parent_frame, text="Ejecutar Monitores de Seguridad", command=self.run_security_monitors)
        run_button.pack(pady=10)

        # Área de texto para mostrar la salida del script
        self.output_text = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, width=70, height=20)
        self.output_text.pack(expand=True, fill="both", padx=10, pady=5)
        self.output_text.insert(tk.END, "Haz clic en 'Ejecutar Monitores de Seguridad' para iniciar el proceso.\n")

        # Etiquetas para el estado de los servicios
        self.service_status_labels = {}
        self.services_to_monitor = ["CloudflareWarp", "WinDefend", "MpsSvc", "croudsec"]
        for service in self.services_to_monitor:
            label = ttk.Label(parent_frame, text=f"{service}: Desconocido")
            label.pack(anchor="w", padx=10)
            self.service_status_labels[service] = label
        
        # Botón para actualizar el estado de los servicios
        refresh_service_button = ttk.Button(parent_frame, text="Actualizar Estado de Servicios", command=self.update_service_statuses_threaded)
        refresh_service_button.pack(pady=5)

        self.update_service_statuses_threaded() # Actualizar estado al iniciar

    def run_security_monitors(self):
        self.output_text.insert(tk.END, "\nIniciando monitores de seguridad...\n")
        self.output_text.see(tk.END)
        
        # Deshabilitar el botón para evitar múltiples ejecuciones
        # (Se re-habilitará al finalizar la ejecución)
        # self.general_status_frame.children['!button'].config(state=tk.DISABLED)

        # Ejecutar el script en un hilo separado para no bloquear la GUI
        threading.Thread(target=self._execute_security_script).start()

    def _execute_security_script(self):
        script_path = "C:\\www\\ciberseguridad\\start_security_monitors.ps1"
        command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            # Leer la salida en tiempo real
            for line in process.stdout:
                self.root.after(0, self._update_output_text, line) # Actualizar la GUI en el hilo principal
            
            process.stdout.close()
            stderr_output = process.stderr.read()
            if stderr_output:
                self.root.after(0, self._update_output_text, f"ERROR:\n{stderr_output}")

            process.wait() # Esperar a que el proceso termine
            self.root.after(0, self._update_output_text, f"\nMonitores de seguridad finalizados con código de salida: {process.returncode}\n")
            self.root.after(0, self.update_service_statuses_threaded) # Actualizar el estado de los servicios al finalizar

        except FileNotFoundError:
            self.root.after(0, self._update_output_text, "Error: powershell.exe no encontrado. Asegúrate de que PowerShell esté instalado y en tu PATH.\n")
        except Exception as e:
            self.root.after(0, self._update_output_text, f"Error al ejecutar el script: {e}\n")
        finally:
            # Re-habilitar el botón
            # self.general_status_frame.children['!button'].config(state=tk.NORMAL)
            pass # Placeholder for now

    def _update_output_text(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def update_service_statuses_threaded(self):
        threading.Thread(target=self._update_service_statuses_actual).start()

    def _update_service_statuses_actual(self):
        for service_name in self.services_to_monitor:
            status = self._get_service_status(service_name)
            self.root.after(0, self._update_service_label, service_name, status)

    def _get_service_status(self, service_name):
        try:
            command = ["sc", "query", service_name]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            output = result.stdout
            if "RUNNING" in output:
                return "En ejecución"
            elif "STOPPED" in output:
                return "Detenido"
            elif "PENDING" in output:
                return "Pendiente"
            else:
                return "Desconocido"
        except subprocess.CalledProcessError as e:
            if "The specified service does not exist" in e.stderr:
                return "No encontrado"
            else:
                return f"Error: {e.stderr.strip()}"
        except Exception as e:
            return f"Error: {e}"

    def _update_service_label(self, service_name, status):
        self.service_status_labels[service_name].config(text=f"{service_name}: {status}")

    def create_security_logs_tab(self, parent_frame):
        log_files = {
            "service_monitor_log.txt": "C:\\www\\ciberseguridad\\service_monitor_log.txt",
            "explorer_window_log.txt": "C:\\www\\ciberseguridad\\explorer_window_log.txt",
            "integrity_check_log.txt": "C:\\www\\ciberseguridad\\integrity_check_log.txt",
            "event_logs_integrity.log": "C:\\www\\ciberseguridad\\event_logs_integrity.log"
        }

        self.log_text_widgets = {}

        for log_name, log_path in log_files.items():
            frame = ttk.LabelFrame(parent_frame, text=log_name)
            frame.pack(fill="both", expand=True, padx=5, pady=5)

            text_widget = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10)
            text_widget.pack(fill="both", expand=True)
            self.log_text_widgets[log_name] = text_widget

        refresh_button = ttk.Button(parent_frame, text="Actualizar Logs", command=self.refresh_logs)
        refresh_button.pack(pady=5)

        self.refresh_logs() # Cargar logs al iniciar la pestaña

    def refresh_logs(self):
        log_files = {
            "service_monitor_log.txt": "C:\\www\\ciberseguridad\\service_monitor_log.txt",
            "explorer_window_log.txt": "C:\\www\\ciberseguridad\\explorer_window_log.txt",
            "integrity_check_log.txt": "C:\\www\\ciberseguridad\\integrity_check_log.txt",
            "event_logs_integrity.log": "C:\\www\\ciberseguridad\\event_logs_integrity.log"
        }

        for log_name, log_path in log_files.items():
            content = self._read_log_file(log_path)
            self.log_text_widgets[log_name].delete(1.0, tk.END)
            self.log_text_widgets[log_name].insert(tk.END, content)
            self.log_text_widgets[log_name].see(tk.END)

    def _read_log_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return f"Archivo de log no encontrado: {file_path}\n"
        except Exception as e:
            return f"Error al leer el archivo {file_path}: {e}\n"

    def create_integrity_tab(self, parent_frame):
        # Botones para calcular y verificar hashes
        calculate_button = ttk.Button(parent_frame, text="Calcular Hashes (Establecer Línea Base)", command=self.calculate_hashes)
        calculate_button.pack(pady=10)

        verify_button = ttk.Button(parent_frame, text="Verificar Integridad", command=self.verify_integrity)
        verify_button.pack(pady=5)

        # Área de texto para mostrar la salida de la verificación de integridad
        self.integrity_output_text = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, width=70, height=20)
        self.integrity_output_text.pack(expand=True, fill="both", padx=10, pady=5)
        self.integrity_output_text.insert(tk.END, "Haz clic en 'Calcular Hashes' para establecer la línea base o en 'Verificar Integridad' para comprobar cambios.\n")

        # Cargar el log de integridad al iniciar la pestaña
        self._load_integrity_log()

    def calculate_hashes(self):
        self.integrity_output_text.insert(tk.END, "\nIniciando cálculo de hashes para C:\\www...\n")
        self.integrity_output_text.see(tk.END)
        threading.Thread(target=self._execute_integrity_script, args=("calculate_www_hashes.ps1",)).start()

    def verify_integrity(self):
        self.integrity_output_text.insert(tk.END, "\nIniciando verificación de integridad para C:\\www...\n")
        self.integrity_output_text.see(tk.END)
        threading.Thread(target=self._execute_integrity_script, args=("verify_www_integrity.ps1",)).start()

    def _execute_integrity_script(self, script_name):
        script_path = os.path.join("C:\\www\\ciberseguridad", script_name)
        command = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
            
            for line in process.stdout:
                self.root.after(0, self._update_integrity_output_text, line)
            
            process.stdout.close()
            stderr_output = process.stderr.read()
            if stderr_output:
                self.root.after(0, self._update_integrity_output_text, f"ERROR:\n{stderr_output}")

            process.wait()
            self.root.after(0, self._update_integrity_output_text, f"\nScript {script_name} finalizado con código de salida: {process.returncode}\n")
            self.root.after(0, self._load_integrity_log) # Recargar el log de integridad al finalizar

        except FileNotFoundError:
            self.root.after(0, self._update_integrity_output_text, "Error: powershell.exe no encontrado.\n")
        except Exception as e:
            self.root.after(0, self._update_integrity_output_text, f"Error al ejecutar el script {script_name}: {e}\n")

    def _update_integrity_output_text(self, text):
        self.integrity_output_text.insert(tk.END, text)
        self.integrity_output_text.see(tk.END)

    def _load_integrity_log(self):
        integrity_log_path = "C:\\www\\ciberseguridad\\integrity_check_log.txt"
        content = self._read_log_file(integrity_log_path)
        self.integrity_output_text.delete(1.0, tk.END)
        self.integrity_output_text.insert(tk.END, content)
        self.integrity_output_text.see(tk.END)

    def create_about_tab(self, parent_frame):
        about_file_path = "C:\\www\\ciberseguridad\\GEMINI_SECURITY_OVERVIEW.md"
        about_content = self._read_log_file(about_file_path)

        about_text = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, width=70, height=20)
        about_text.pack(expand=True, fill="both", padx=10, pady=5)
        about_text.insert(tk.END, about_content)
        about_text.config(state=tk.DISABLED) # Hacer el texto de solo lectura


if __name__ == "__main__":
    root = tk.Tk()
    app = SecurityMonitorApp(root)
    root.mainloop()
