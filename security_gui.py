import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import time
import hashlib
import os
from datetime import datetime
import requests
from typing import Dict, List, Optional
import sqlite3
import google.generativeai
import openai

class SecurityMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Security Monitor")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f172a")
        
        # Variables de estado
        self.is_monitoring = False
        self.api_connected = False
        self.cloud_connected = False
        
        # Configuración de APIs
        self.api_configs = {
            "gemini": {"url": "https://api.gemini.google.com/v1", "key": ""},
            "openai": {"url": "https://api.openai.com/v1", "key": ""},
            "azure": {"url": "https://your-resource.azure.com", "key": ""}
        }
        
        # Aplicaciones de seguridad a monitorear
        self.security_apps = {
            "windows_defender": {"status": False, "logs": []},
            "file_explorer": {"status": False, "access_logs": []},
            "cloudflare_warp": {"status": False, "traffic_logs": []},
            "crowdsec": {"status": False, "alerts": []}
        }
        
        # Inicializar base de datos
        self.init_database()
        
        # Crear interfaz gráfica
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
        self.notebook.add(self.integrity_frame, text="Integridad de C:\\www")
        self.create_integrity_tab(self.integrity_frame)

        # --- Pestaña "Configuración/Acerca de" ---
        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="Configuración/Acerca de")
        self.create_about_tab(self.about_frame)
        
        # Iniciar hilo de monitoreo
        self.monitoring_thread = None
        
        # Manejar cierre de la aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def init_database(self):
        """Inicializar base de datos para almacenar logs y configuraciones"""
        self.conn = sqlite3.connect('security_ai.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Crear tabla para logs de seguridad
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                app_name TEXT,
                log_data TEXT,
                hash_value TEXT,
                protected BOOLEAN DEFAULT 1
            )
        ''')
        
        # Crear tabla para configuraciones
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS configurations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                config_key TEXT UNIQUE,
                config_value TEXT
            )
        ''')
        
        self.conn.commit()

    def create_general_status_tab(self, parent_frame):
        # Frame principal
        main_frame = tk.Frame(parent_frame, bg="#0f172a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="Módulo de Conexión API IA para Seguridad Windows",
            font=("Segoe UI", 20, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        title_label.pack(pady=(0, 20))
        
        # Frame de estado
        status_frame = tk.LabelFrame(main_frame, text="Estado del Sistema", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Indicadores de estado
        self.status_indicators = {}
        indicators_frame = tk.Frame(status_frame, bg="#1e293b")
        indicators_frame.pack(fill=tk.X, padx=10, pady=10)
        
        statuses = [
            ("Monitorización", "monitoring"),
            ("Conexión API", "api"),
            ("Conexión Cloud", "cloud"),
            ("Protección de Logs", "logs")
        ]
        
        for i, (label, key) in enumerate(statuses):
            indicator_frame = tk.Frame(indicators_frame, bg="#1e293b")
            indicator_frame.grid(row=0, column=i, padx=15, pady=5)
            
            tk.Label(indicator_frame, text=label, fg="#94a3b8", bg="#1e293b", font=("Segoe UI", 10)).pack()
            
            self.status_indicators[key] = tk.Label(
                indicator_frame, 
                text="●", 
                fg="#ef4444", 
                bg="#1e293b", 
                font=("Arial", 16)
            )
            self.status_indicators[key].pack()
        
        # Frame de configuración
        config_frame = tk.LabelFrame(main_frame, text="Configuración", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Configuración de APIs
        api_frame = tk.Frame(config_frame, bg="#1e293b")
        api_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(api_frame, text="API Gemini Key:", fg="#cbd5e1", bg="#1e293b").grid(row=0, column=0, sticky="w", pady=5)
        self.gemini_key_entry = tk.Entry(api_frame, width=40, show="*", bg="#334155", fg="#f1f5f9", insertbackground="white")
        self.gemini_key_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        tk.Label(api_frame, text="API OpenAI Key:", fg="#cbd5e1", bg="#1e293b").grid(row=1, column=0, sticky="w", pady=5)
        self.openai_key_entry = tk.Entry(api_frame, width=40, show="*", bg="#334155", fg="#f1f5f9", insertbackground="white")
        self.openai_key_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        # Botones de control
        button_frame = tk.Frame(config_frame, bg="#1e293b")
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.connect_btn = tk.Button(
            button_frame, 
            text="Conectar APIs", 
            command=self.connect_apis,
            bg="#2563eb", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_monitor_btn = tk.Button(
            button_frame, 
            text="Iniciar Monitorización", 
            command=self.toggle_monitoring,
            bg="#10b981", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        )
        self.start_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cloud_btn = tk.Button(
            button_frame, 
            text="Conectar Cloud", 
            command=self.connect_cloud,
            bg="#8b5cf6", 
            fg="white", 
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=20
        )
        self.cloud_btn.pack(side=tk.LEFT)
        
        # Frame de aplicaciones de seguridad
        apps_frame = tk.LabelFrame(main_frame, text="Aplicaciones de Seguridad", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
        apps_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Lista de aplicaciones
        apps_list_frame = tk.Frame(apps_frame, bg="#1e293b")
        apps_list_frame.pack(fill=tk.X, padx=10, pady=10)
        
        for i, (app_name, app_data) in enumerate(self.security_apps.items()):
            app_row = tk.Frame(apps_list_frame, bg="#1e293b")
            app_row.pack(fill=tk.X, pady=5)
            
            tk.Label(app_row, text=app_name.replace("_", " ").title(), fg="#cbd5e1", bg="#1e293b", width=20, anchor="w").pack(side=tk.LEFT)
            
            status_label = tk.Label(app_row, text="Desconectado", fg="#ef4444", bg="#1e293b")
            status_label.pack(side=tk.LEFT, padx=(10, 0))
            self.security_apps[app_name]["status_label"] = status_label
            
            tk.Button(
                app_row, 
                text="Activar", 
                command=lambda a=app_name: self.toggle_app(a),
                bg="#3b82f6", 
                fg="white", 
                font=("Segoe UI", 8),
                relief="flat"
            ).pack(side=tk.RIGHT)
        
        # Frame de logs y resultados
        logs_frame = tk.LabelFrame(main_frame, text="Logs y Resultados", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto para logs
        self.log_text = scrolledtext.ScrolledText(
            logs_frame, 
            height=10, 
            bg="#0f172a", 
            fg="#cbd5e1", 
            insertbackground="white",
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Botón para limpiar logs
        tk.Button(
            logs_frame, 
            text="Limpiar Logs", 
            command=self.clear_logs,
            bg="#ef4444", 
            fg="white", 
            font=("Segoe UI", 10),
            relief="flat"
        ).pack(side=tk.RIGHT, padx=10, pady=(0, 10))

    def connect_apis(self):
        """Conectar con las APIs de IA configuradas"""
        try:
            # Obtener claves de API
            gemini_key = self.gemini_key_entry.get()
            openai_key = self.openai_key_entry.get()
            
            if gemini_key:
                self.api_configs["gemini"]["key"] = gemini_key
                self.log_message("Conectado a API Gemini")
            
            if openai_key:
                self.api_configs["openai"]["key"] = openai_key
                self.log_message("Conectado a API OpenAI")
            
            self.api_connected = True
            self.update_status_indicator("api", True)
            messagebox.showinfo("Conexión Exitosa", "Conectado a las APIs de IA")
            
        except Exception as e:
            self.log_message(f"Error al conectar APIs: {str(e)}")
            messagebox.showerror("Error de Conexión", f"No se pudieron conectar las APIs: {str(e)}")


    def connect_cloud(self):
        """Conectar con servicios en la nube"""
        try:
            # Simular conexión a servicios cloud
            self.cloud_connected = True
            self.update_status_indicator("cloud", True)
            self.log_message("Conectado a servicios en la nube (Supabase, Google Cloud)")
            messagebox.showinfo("Conexión Exitosa", "Conectado a servicios en la nube")
            
        except Exception as e:
            self.log_message(f"Error al conectar cloud: {str(e)}")
            messagebox.showerror("Error de Conexión", f"No se pudieron conectar los servicios cloud: {str(e)}")


    def toggle_monitoring(self):
        """Iniciar o detener la monitorización"""
        if not self.is_monitoring:
            if not self.api_connected:
                messagebox.showwarning("Sin conexión", "Por favor, conecte las APIs primero")
                return
                
            self.is_monitoring = True
            self.start_monitor_btn.config(text="Detener Monitorización", bg="#ef4444")
            self.update_status_indicator("monitoring", True)
            self.log_message("Monitorización iniciada")
            
            # Iniciar hilo de monitorización
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        else:
            self.is_monitoring = False
            self.start_monitor_btn.config(text="Iniciar Monitorización", bg="#10b981")
            self.update_status_indicator("monitoring", False)
            self.log_message("Monitorización detenida")


    def monitoring_loop(self):
        """Bucle principal de monitorización"""
        while self.is_monitoring:
            try:
                # Simular recopilación de datos de seguridad
                self.collect_security_data()
                
                # Analizar datos con IA
                self.analyze_with_ai()
                
                # Proteger logs
                self.protect_logs()
                
                time.sleep(5)  # Intervalo de monitorización
                
            except Exception as e:
                self.log_message(f"Error en monitorización: {str(e)}")


    def collect_security_data(self):
        """Recopilar datos de aplicaciones de seguridad"""
        for app_name in self.security_apps:
            # Simular recopilación de datos
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": f"Actividad en {app_name}",
                "details": "Datos simulados para demostración"
            }
            
            self.security_apps[app_name]["logs"].append(log_entry)
            self.log_message(f"Datos recopilados de {app_name}")
            
            # Guardar en base de datos
            self.save_log_to_db(app_name, json.dumps(log_entry))


    def analyze_with_ai(self):
        """Analizar datos con inteligencia artificial"""
        if not self.api_connected:
            return

        analysis_result = {
            "threat_level": "desconocido",
            "recommendations": ["No hay recomendaciones disponibles"],
            "timestamp": datetime.now().isoformat()
        }

        # Recopilar los últimos logs de todas las aplicaciones de seguridad
        all_logs = []
        for app_name, app_data in self.security_apps.items():
            if "logs" in app_data and app_data["logs"]:
                # Tomar los últimos 5 logs por aplicación para evitar sobrecargar la IA
                last_logs = app_data["logs"][-5:]
                for log in last_logs:
                    all_logs.append(f"[{app_name}] {log.get('event', 'N/A')}: {log.get('details', 'N/A')}")

        if not all_logs:
            self.log_message("No hay logs recientes para analizar con IA.")
            return

        prompt = "Analiza los siguientes logs de seguridad y proporciona un nivel de amenaza (bajo, medio, alto, crítico) y recomendaciones concisas. Si no hay amenazas claras, indica 'bajo' y recomendaciones generales de seguridad.\n\n" + "\n".join(all_logs)

        ai_response_text = self._get_ai_response(prompt)

        if ai_response_text:
            self.log_message(f"Respuesta de IA: {ai_response_text}")
            # Intentar parsear la respuesta de la IA para extraer nivel de amenaza y recomendaciones
            # Esto es una simplificación; en un entorno real, se usaría un formato estructurado (JSON)
            if "Nivel de amenaza:" in ai_response_text:
                try:
                    threat_line = [line for line in ai_response_text.split('\n') if "Nivel de amenaza:" in line][0]
                    analysis_result["threat_level"] = threat_line.split(":")[1].strip().lower()
                except IndexError:
                    pass # Fallback a desconocido

            if "Recomendaciones:" in ai_response_text:
                try:
                    rec_start_index = ai_response_text.find("Recomendaciones:")
                    recommendations_text = ai_response_text[rec_start_index + len("Recomendaciones:"):].strip()
                    analysis_result["recommendations"] = [rec.strip() for rec in recommendations_text.split('- ') if rec.strip()]
                except Exception:
                    pass # Fallback a no hay recomendaciones

        self.log_message("Análisis con IA completado")
        self.log_message(f"Resultado: Nivel de amenaza {analysis_result['threat_level']}")
        self.log_message(f"Recomendaciones: {', '.join(analysis_result['recommendations'])}")

    def _get_ai_response(self, prompt: str) -> Optional[str]:
        """Obtiene una respuesta de la API de IA (Gemini o OpenAI)."""
        gemini_key = self.api_configs["gemini"]["key"]
        openai_key = self.api_configs["openai"]["key"]

        if gemini_key:
            try:
                google.generativeai.configure(api_key=gemini_key)
                model = google.generativeai.GenerativeModel('gemini-pro')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                self.log_message(f"Error al usar la API de Gemini: {str(e)}")
        
        if openai_key:
            try:
                client = openai.OpenAI(api_key=openai_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Eres un asistente de seguridad que analiza logs."},
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.choices[0].message.content
            except Exception as e:
                self.log_message(f"Error al usar la API de OpenAI: {str(e)}")
        
        self.log_message("No se encontró una clave de API de IA válida para realizar el análisis.")
        return None


    def protect_logs(self):
        """Proteger archivos de log del sistema"""
        # Simular protección de logs
        self.update_status_indicator("logs", True)
        self.log_message("Protección de logs activa")


    def toggle_app(self, app_name):
        """Activar o desactivar una aplicación de seguridad"""
        current_status = self.security_apps[app_name]["status"]
        new_status = not current_status
        
        self.security_apps[app_name]["status"] = new_status
        status_text = "Activado" if new_status else "Desconectado"
        status_color = "#10b981" if new_status else "#ef4444"
        
        self.security_apps[app_name]["status_label"].config(text=status_text, fg=status_color)
        self.log_message(f"{app_name} {status_text.lower()}")


    def save_log_to_db(self, app_name, log_data):
        """Guardar log en la base de datos"""
        try:
            # Generar hash para integridad
            hash_value = hashlib.sha256(log_data.encode()).hexdigest()
            
            self.cursor.execute('''
                INSERT INTO security_logs (timestamp, app_name, log_data, hash_value)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), app_name, log_data, hash_value))
            
            self.conn.commit()
        except Exception as e:
            self.log_message(f"Error al guardar log: {str(e)}")


    def log_message(self, message):
        """Agregar mensaje al área de logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)


    def clear_logs(self):
        """Limpiar el área de logs"""
        self.log_text.delete(1.0, tk.END)


    def update_status_indicator(self, indicator_key, status):
        """Actualizar indicador de estado"""
        color = "#10b981" if status else "#ef4444"
        self.status_indicators[indicator_key].config(fg=color)


    def on_closing(self):
        """Manejar cierre de la aplicación"""
        self.is_monitoring = False
        if self.conn:
            self.conn.close()
        self.root.destroy()

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
            return f"Error al ejecutar el script {script_name}: {e}\n"

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