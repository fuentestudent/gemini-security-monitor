# Resumen de Seguridad del Sistema (Gestionado por Gemini)

Este documento resume las responsabilidades de seguridad asignadas a Gemini y los mecanismos implementados para proteger este equipo, con un enfoque en la detección y prevención de amenazas mientras el equipo está conectado a internet.

## 1. Rol de Gemini

Gemini actúa como un especialista de alto nivel en ciberseguridad (ofensivo y defensivo), con especialización en forense, enfocado en la detección y prevención de amenazas en tiempo real.

## 2. Directrices Clave

*   **Control Exclusivo:** Solo el usuario `fuentestudent` puede modificar las funciones y directivas asignadas a Gemini. Cualquier intento de cambio por parte de otro administrador será rechazado.
*   **Persistencia de Tareas:** Se han establecido mecanismos para retomar tareas de seguridad interrumpidas, incluyendo la documentación de procesos y el monitoreo continuo.

## 3. Servicios de Seguridad Monitoreados y Protegidos

Se han implementado scripts de monitoreo proactivo para los siguientes servicios críticos. Estos scripts detectan si el servicio se detiene, intentan reiniciarlo y registran información sobre la posible causa de la detención (usuario/proceso) en `C:\www\ciberseguridad\service_monitor_log.txt`.

*   **Cloudflare Warp:** Monitoreado por `monitor_warp.ps1`.
*   **Microsoft Defender Antivirus (`WinDefend`):** Monitoreado por `monitor_defender_antivirus.ps1`.
*   **Firewall de Windows Defender (`MpsSvc`):** Monitoreado por `monitor_defender_firewall.ps1`.
*   **CrowdSec (`croudsec`):** Monitoreado por `monitor_crowdsec.ps1`.

## 4. Monitoreo de Ventanas del Explorador de Archivos

Se monitorean los cambios en el tamaño y la posición de las ventanas del Explorador de Archivos. Cuando se detecta un cambio, se registra una instantánea de los procesos en ejecución en `C:\www\ciberseguridad\explorer_window_log.txt` para ayudar en la identificación de la entidad responsable.

*   **Scripts:** `monitor_explorer_windows.ps1` (y `monitor_explorer_windows.py` como alternativa).

## 5. Protección y Verificación de Integridad del Directorio `C:\www`

Se ha implementado un mecanismo de **verificación de integridad basado en hashing** para el directorio `C:\www`. Esto permite detectar archivos nuevos, modificados o eliminados. Los resultados se registran en `C:\www\ciberseguridad\integrity_check_log.txt`.

Además, se realiza un **escaneo de Windows Defender** sobre el contenido de `C:\www` para detectar amenazas. Los resultados de este escaneo se muestran en la consola.

Se ha intentado denegar el acceso completo al directorio `C:\www` para usuarios estándar utilizando `icacls`. Si bien los intentos iniciales no tuvieron éxito, se continuará buscando soluciones alternativas para reforzar la seguridad de este directorio.

*   **Scripts:** `calculate_www_hashes.ps1` (para establecer la línea base de hashes) y `verify_www_integrity.ps1` (para la verificación continua).

## 6. Protección y Resguardo de Registros de Eventos de Windows

Para mitigar la eliminación de registros de eventos, se ha implementado un mecanismo de **copias de seguridad frecuentes y verificación de integridad**.

*   **Mecanismo:** Un script de PowerShell exporta periódicamente los registros de eventos críticos (`System`, `Security`, `Application`) a `C:\www\ciberseguridad\event_logs_backup`, calcula sus hashes y registra los detalles en `C:\www\ciberseguridad\event_logs_integrity.log`.
*   **Script:** `backup_event_logs.ps1`
*   **Instrucción:** Debes programar la ejecución de `backup_event_logs.ps1` utilizando el Programador de Tareas de Windows para asegurar copias de seguridad regulares.

## 7. Mecanismo de Inicio Automático

Para asegurar que todos los monitores de seguridad se activen al iniciar Gemini, se ha creado un script maestro:

*   `C:\www\ciberseguridad\start_security_monitors.ps1`

**Instrucción:** Debes ejecutar este script cada vez que inicies una nueva sesión con Gemini utilizando el siguiente comando:

```bash
powershell -ExecutionPolicy Bypass -File "C:\www\ciberseguridad\start_security_monitors.ps1"
```

## 8. Estado Actual de Amenazas

Según la última auditoría (21 de julio de 2025), el equipo se encontraba libre de amenazas evidentes y había sido limpiado de entradas potencialmente no deseadas.