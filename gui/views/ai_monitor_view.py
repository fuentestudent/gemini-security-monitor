import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from backend.ai_integration import AISecurityCore

def create_ai_monitor_view(parent_frame):
    ai_monitor_frame = ttk.Frame(parent_frame, style='TFrame')
    ai_monitor_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Initialize AISecurityCore with callbacks
    ai_core = AISecurityCore(
        log_callback=lambda msg: log_message(msg, log_text),
        status_update_callback=lambda key, status: update_status_indicator(key, status, status_indicators)
    )

    # Título
    title_label = tk.Label(
        ai_monitor_frame,
        text="Módulo de Conexión API IA para Seguridad Windows",
        font=("Segoe UI", 20, "bold"),
        fg="#38bdf8",
        bg="#0f172a"
    )
    title_label.pack(pady=(0, 20))

    # Frame de estado
    status_frame = tk.LabelFrame(ai_monitor_frame, text="Estado del Sistema", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
    status_frame.pack(fill=tk.X, pady=(0, 20))

    # Indicadores de estado
    status_indicators = {}
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

        status_indicators[key] = tk.Label(
            indicator_frame,
            text="●",
            fg="#ef4444",
            bg="#1e293b",
            font=("Arial", 16)
        )
        status_indicators[key].pack()

    # Frame de configuración
    config_frame = tk.LabelFrame(ai_monitor_frame, text="Configuración", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
    config_frame.pack(fill=tk.X, pady=(0, 20))

    # Configuración de APIs
    api_frame = tk.Frame(config_frame, bg="#1e293b")
    api_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(api_frame, text="API Gemini Key:", fg="#cbd5e1", bg="#1e293b").grid(row=0, column=0, sticky="w", pady=5)
    gemini_key_entry = tk.Entry(api_frame, width=40, show="*", bg="#334155", fg="#f1f5f9", insertbackground="white")
    gemini_key_entry.grid(row=0, column=1, padx=(10, 0), pady=5)

    tk.Label(api_frame, text="API OpenAI Key:", fg="#cbd5e1", bg="#1e293b").grid(row=1, column=0, sticky="w", pady=5)
    openai_key_entry = tk.Entry(api_frame, width=40, show="*", bg="#334155", fg="#f1f5f9", insertbackground="white")
    openai_key_entry.grid(row=1, column=1, padx=(10, 0), pady=5)

    # Botones de control
    button_frame = tk.Frame(config_frame, bg="#1e293b")
    button_frame.pack(fill=tk.X, padx=10, pady=10)

    def connect_apis_action():
        ai_core.set_api_keys(gemini_key_entry.get(), openai_key_entry.get())
        if ai_core.connect_apis():
            messagebox.showinfo("Conexión Exitosa", "Conectado a las APIs de IA")
        else:
            messagebox.showerror("Error de Conexión", "No se pudieron conectar las APIs. Verifique las claves.")

    connect_btn = tk.Button(
        button_frame,
        text="Conectar APIs",
        command=connect_apis_action,
        bg="#2563eb",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=20
    )
    connect_btn.pack(side=tk.LEFT, padx=(0, 10))

    def toggle_monitoring_action():
        if ai_core.toggle_monitoring():
            start_monitor_btn.config(text="Detener Monitorización", bg="#ef4444")
        else:
            start_monitor_btn.config(text="Iniciar Monitorización", bg="#10b981")

    start_monitor_btn = tk.Button(
        button_frame,
        text="Iniciar Monitorización",
        command=toggle_monitoring_action,
        bg="#10b981",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=20
    )
    start_monitor_btn.pack(side=tk.LEFT, padx=(0, 10))

    def connect_cloud_action():
        if ai_core.connect_cloud():
            messagebox.showinfo("Conexión Exitosa", "Conectado a servicios en la nube")
        else:
            messagebox.showerror("Error de Conexión", "No se pudieron conectar los servicios cloud.")

    cloud_btn = tk.Button(
        button_frame,
        text="Conectar Cloud",
        command=connect_cloud_action,
        bg="#8b5cf6",
        fg="white",
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        padx=20
    )
    cloud_btn.pack(side=tk.LEFT)

    # Frame de aplicaciones de seguridad
    apps_frame = tk.LabelFrame(ai_monitor_frame, text="Aplicaciones de Seguridad", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
    apps_frame.pack(fill=tk.X, pady=(0, 20))

    # Lista de aplicaciones
    apps_list_frame = tk.Frame(apps_frame, bg="#1e293b")
    apps_list_frame.pack(fill=tk.X, padx=10, pady=10)

    app_status_labels = {}
    for app_name in ai_core.security_apps.keys():
        app_row = tk.Frame(apps_list_frame, bg="#1e293b")
        app_row.pack(fill=tk.X, pady=5)

        tk.Label(app_row, text=app_name.replace("_", " ").title(), fg="#cbd5e1", bg="#1e293b", width=20, anchor="w").pack(side=tk.LEFT)

        status_label = tk.Label(app_row, text="Desconectado", fg="#ef4444", bg="#1e293b")
        status_label.pack(side=tk.LEFT, padx=(10, 0))
        app_status_labels[app_name] = status_label

        def toggle_app_action(name=app_name):
            current_status = ai_core.security_apps[name]["status"]
            new_status = not current_status
            if ai_core.toggle_app_status(name, new_status):
                status_text = "Activado" if new_status else "Desconectado"
                status_color = "#10b981" if new_status else "#ef4444"
                app_status_labels[name].config(text=status_text, fg=status_color)

        tk.Button(
            app_row,
            text="Activar",
            command=toggle_app_action,
            bg="#3b82f6",
            fg="white",
            font=("Segoe UI", 8),
            relief="flat"
        ).pack(side=tk.RIGHT)

    # Frame de logs y resultados
    logs_frame = tk.LabelFrame(ai_monitor_frame, text="Logs y Resultados", bg="#1e293b", fg="#94a3b8", font=("Segoe UI", 12, "bold"))
    logs_frame.pack(fill=tk.BOTH, expand=True)

    # Área de texto para logs
    log_text = scrolledtext.ScrolledText(
        logs_frame,
        height=10,
        bg="#0f172a",
        fg="#cbd5e1",
        insertbackground="white",
        font=("Consolas", 9)
    )
    log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Botón para limpiar logs
    def clear_logs_action():
        log_text.delete(1.0, tk.END)

    tk.Button(
        logs_frame,
        text="Limpiar Logs",
        command=clear_logs_action,
        bg="#ef4444",
        fg="white",
        font=("Segoe UI", 10),
        relief="flat"
    ).pack(side=tk.RIGHT, padx=10, pady=(0, 10))

    def log_message(message, text_widget):
        text_widget.insert(tk.END, message + "\n")
        text_widget.see(tk.END)

    def update_status_indicator(indicator_key, status, indicators_dict):
        color = "#10b981" if status else "#ef4444"
        if indicator_key in indicators_dict:
            indicators_dict[indicator_key].config(fg=color)

    # Handle closing to ensure database connection is closed
    def on_closing():
        ai_core.close_connection()
        parent_frame.destroy()

    # This part needs to be handled by the main_window or the app's main loop
    # parent_frame.winfo_toplevel().protocol("WM_DELETE_WINDOW", on_closing)
