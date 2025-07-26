import threading
import json
import time
import hashlib
import os
from datetime import datetime
import requests
from typing import Dict, List, Optional
import sqlite3

class AISecurityCore:
    def __init__(self, log_callback=None, status_update_callback=None):
        self.is_monitoring = False
        self.api_connected = False
        self.cloud_connected = False

        self.api_configs = {
            "gemini": {"url": "https://api.gemini.google.com/v1", "key": ""},
            "openai": {"url": "https://api.openai.com/v1", "key": ""},
            "azure": {"url": "https://your-resource.azure.com", "key": ""}
        }

        self.security_apps = {
            "windows_defender": {"status": False, "logs": []},
            "file_explorer": {"status": False, "access_logs": []},
            "cloudflare_warp": {"status": False, "traffic_logs": []},
            "crowdsec": {"status": False, "alerts": []}
        }

        self.conn = None
        self.cursor = None
        self.init_database()

        self.monitoring_thread = None

        # Callbacks for GUI updates
        self.log_callback = log_callback if log_callback else print
        self.status_update_callback = status_update_callback if status_update_callback else self._default_status_update

    def _default_status_update(self, indicator_key, status):
        print(f"Status update for {indicator_key}: {'Active' if status else 'Inactive'}")

    def init_database(self):
        """Inicializar base de datos para almacenar logs y configuraciones"""
        try:
            self.conn = sqlite3.connect('security_ai.db', check_same_thread=False)
            self.cursor = self.conn.cursor()

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

            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS configurations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_key TEXT UNIQUE,
                    config_value TEXT
                )
            ''')
            self.conn.commit()
            self.log_message("Base de datos inicializada correctamente.")
        except Exception as e:
            self.log_message(f"Error al inicializar la base de datos: {str(e)}")

    def set_api_keys(self, gemini_key, openai_key):
        if gemini_key:
            self.api_configs["gemini"]["key"] = gemini_key
            self.log_message("Clave de API Gemini configurada.")
        if openai_key:
            self.api_configs["openai"]["key"] = openai_key
            self.log_message("Clave de API OpenAI configurada.")

    def connect_apis(self):
        """Conectar con las APIs de IA configuradas"""
        try:
            # In a real scenario, you would validate keys here
            if self.api_configs["gemini"]["key"] or self.api_configs["openai"]["key"]:
                self.api_connected = True
                self.status_update_callback("api", True)
                self.log_message("Conectado a las APIs de IA.")
                return True
            else:
                self.log_message("No se han configurado claves de API.")
                return False
        except Exception as e:
            self.log_message(f"Error al conectar APIs: {str(e)}")
            return False

    def connect_cloud(self):
        """Conectar con servicios en la nube"""
        try:
            # Simular conexión a servicios cloud
            self.cloud_connected = True
            self.status_update_callback("cloud", True)
            self.log_message("Conectado a servicios en la nube (Supabase, Google Cloud).")
            return True
        except Exception as e:
            self.log_message(f"Error al conectar cloud: {str(e)}")
            return False

    def toggle_monitoring(self):
        """Iniciar o detener la monitorización"""
        if not self.is_monitoring:
            if not self.api_connected:
                self.log_message("Error: APIs no conectadas. No se puede iniciar la monitorización.")
                return False

            self.is_monitoring = True
            self.status_update_callback("monitoring", True)
            self.log_message("Monitorización iniciada.")

            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            return True
        else:
            self.is_monitoring = False
            self.status_update_callback("monitoring", False)
            self.log_message("Monitorización detenida.")
            return False

    def monitoring_loop(self):
        """Bucle principal de monitorización"""
        while self.is_monitoring:
            try:
                self.collect_security_data()
                self.analyze_with_ai()
                self.protect_logs()
                time.sleep(5)
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

            self.save_log_to_db(app_name, json.dumps(log_entry))

    def analyze_with_ai(self):
        """Analizar datos con inteligencia artificial"""
        if not self.api_connected:
            return

        # Simular análisis con IA
        analysis_result = {
            "threat_level": "bajo",
            "recommendations": ["Mantener vigilancia", "Actualizar definiciones de virus"],
            "timestamp": datetime.now().isoformat()
        }

        self.log_message("Análisis con IA completado.")
        self.log_message(f"Resultado: Nivel de amenaza {analysis_result['threat_level']}.")

    def protect_logs(self):
        """Proteger archivos de log del sistema"""
        self.status_update_callback("logs", True)
        self.log_message("Protección de logs activa.")

    def toggle_app_status(self, app_name, status):
        """Actualizar el estado de una aplicación de seguridad"""
        if app_name in self.security_apps:
            self.security_apps[app_name]["status"] = status
            status_text = "Activado" if status else "Desconectado"
            self.log_message(f"{app_name} {status_text.lower()}")
            return True
        return False

    def save_log_to_db(self, app_name, log_data):
        """Guardar log en la base de datos"""
        try:
            hash_value = hashlib.sha256(log_data.encode()).hexdigest()

            self.cursor.execute('''
                INSERT INTO security_logs (timestamp, app_name, log_data, hash_value)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), app_name, log_data, hash_value))

            self.conn.commit()
        except Exception as e:
            self.log_message(f"Error al guardar log en DB: {str(e)}")

    def log_message(self, message):
        """Agregar mensaje al área de logs (usando el callback)"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        if self.log_callback:
            self.log_callback(formatted_message)

    def close_connection(self):
        """Cerrar la conexión a la base de datos"""
        self.is_monitoring = False # Ensure monitoring loop stops
        if self.conn:
            self.conn.close()
            self.log_message("Conexión a la base de datos cerrada.")
