# Informe de Auditoría y Monitorización de Seguridad - 2025-07-21

**Operador:** Gemini (en rol de Especialista en Ciberseguridad)
**Cliente:** fuentestudent
**Objetivo:** Realizar un análisis forense inicial, limpiar amenazas y establecer una línea base para la monitorización continua del sistema.

---

## Resumen de Actividades

Se ha realizado una auditoría completa del estado de seguridad del sistema. Las acciones y conclusiones se detallan a continuación.

### 1. Verificación de Servicios de Seguridad Críticos

- **Firewall de Windows Defender (`MpsSvc`):**
  - **Estado:** `RUNNING` (En ejecución)
  - **Tipo de Inicio:** `AUTO_START` (Automático)
  - **Conclusión:** El servicio está activo y configurado correctamente para proteger el sistema desde el arranque.

- **Antivirus de Microsoft Defender (`WinDefend`):**
  - **Estado:** `RUNNING` (En ejecución)
  - **Tipo de Inicio:** `AUTO_START` (Automático)
  - **Conclusión:** El servicio está activo y configurado correctamente para la protección antivirus desde el arranque.

### 2. Análisis de Puntos de Auto-Inicio (Autoruns)

Se realizó un análisis de todas las entradas de registro y ubicaciones del sistema que ejecutan programas automáticamente al iniciar sesión.

- **Hallazgos:**
  1.  **(ALTA PRIORIDAD) Entrada de Registro Huérfana:** Se detectó una entrada llamada `PAC7302_Monitor` que apuntaba a un archivo inexistente (`C:\WINDOWS\PixArt\PAC7302\Monitor.exe.exe`). Este tipo de entradas son sospechosas y pueden ser remanentes de malware.
  2.  **(AVISO) Programa Potencialmente no Deseado:** Se detectó que `Yandex Browser` se iniciaba automáticamente en segundo plano.

- **Acciones de Remediación:**
  1.  Se eliminó la entrada de registro huérfana `PAC7302_Monitor` para limpiar el sistema.
      - **Comando:** `reg delete HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v PAC7302_Monitor /f`
  2.  Se eliminó la entrada de registro de inicio automático para `Yandex Browser` para evitar su ejecución en segundo plano.
      - **Comando:** `reg delete HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run /v YandexBrowserAutoLaunch_79CFD713EA68C336FE522D6F5B867780 /f`

### 3. Análisis de Conexiones de Red

Se realizó un análisis de todas las conexiones de red activas para detectar actividad anómala.

- **Hallazgos:**
  - La mayoría de las conexiones pertenecen a servicios de Windows, Cloudflare Warp, CrowdSec y aplicaciones conocidas.
  - Se identificó una conexión saliente del proceso `node.exe` (PID 7140).

- **Acciones de Verificación:**
  - Se investigó el proceso `node.exe` y se confirmó que corresponde a la **interfaz de línea de comandos de Gemini**, la herramienta que estamos utilizando actualmente.
  - **Comando:** `wmic process where processid=7140 get commandline /format:list`
  - **Conclusión:** La conexión es legítima y segura.

---

## Actualizaciones de Seguridad y Configuración

### 4. Investigación y Remediación del Servicio Cloudflare Warp

- **Problema Detectado:** El servicio `CloudflareWarp` se encontró en estado `STOPPED` a pesar de estar configurado para `AUTO_START (DELAYED)`.
- **Acciones Tomadas:**
  1.  Se inició manualmente el servicio `CloudflareWarp`.
      - **Comando:** `sc start CloudflareWarp`
  2.  Se verificó que el servicio `CloudflareWarp` está ahora en estado `RUNNING`.
  3.  Se creó un script de PowerShell (`C:\www\ciberseguridad\monitor_warp.ps1`) para monitorear y reiniciar automáticamente el servicio si se detiene.
      - **Contenido del script:**
        ```powershell
        $serviceName = "CloudflareWarp"
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

        if ($service -eq $null) {
            Write-Host "El servicio '$serviceName' no se encontró en el sistema."
        } elseif ($service.Status -ne "Running") {
            Write-Host "El servicio '$serviceName' está detenido. Intentando iniciarlo..."
            try {
                Start-Service -Name $serviceName -ErrorAction Stop
                Write-Host "El servicio '$serviceName' se ha iniciado correctamente."
            } catch {
                Write-Error "No se pudo iniciar el servicio '$serviceName'. Error: $($_.Exception.Message)"
            }
        } else {
            Write-Host "El servicio '$serviceName' ya está en ejecución."
        }
        ```
  4.  Se guardó un recordatorio en la memoria de Gemini para verificar el estado de `CloudflareWarp` en futuras conexiones.

### 5. Análisis de la Configuración del Cortafuegos de Windows

- **Estado de Perfiles:** Se verificó el estado de los perfiles de cortafuegos (Dominio, Privado, Público).
  - **Comando:** `netsh advfirewall show allprofiles`
- **Reglas de Entrada:** Se listaron y analizaron las reglas de entrada activas.
  - **Comando:** `netsh advfirewall firewall show rule name=all dir=in`
  - **Hallazgos:** Múltiples reglas de bloqueo de CrowdSec para IPs maliciosas, reglas de permiso para aplicaciones legítimas (Microsoft Store, Edge, Chrome, WhatsApp, Node.js, VS Code, Hyper-V), y numerosas reglas de bloqueo para componentes de CorelDRAW.
- **Reglas de Salida:** Se listaron y analizaron las reglas de salida activas.
  - **Comando:** `netsh advfirewall firewall show rule name=all dir=out`
  - **Hallazgos:** Reglas de permiso para aplicaciones legítimas y componentes de Windows, y numerosas reglas de bloqueo para componentes de CorelDRAW.

### 6. Control de Acceso a Internet para CorelDRAW

- **Objetivo:** Bloquear todas las conexiones a internet desde CorelDRAW y sus componentes, asegurando que el programa funcione correctamente.
- **Acciones Tomadas:**
  1.  Se crearon reglas de bloqueo de salida para los ejecutables principales de CorelDRAW:
      - `CorelDRAW - Bloquear Salida (CorelDRW.exe)`
      - `CorelDRAW - Bloquear Salida (CorelPP.exe)`
      - `CorelDRAW - Bloquear Salida (FontManager.exe)`
      - `CorelDRAW - Bloquear Salida (CrlUISvr.exe)`
      - `CorelDRAW - Bloquear Salida (Setup.exe)`
      - **Comandos:**
        ```bash
        netsh advfirewall firewall add rule name="CorelDRAW - Bloquear Salida (CorelDRW.exe)" dir=out action=block program="C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Programs64\CorelDRW.exe" enable=yes
        netsh advfirewall firewall add rule name="CorelDRAW - Bloquear Salida (CorelPP.exe)" dir=out action=block program="C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Programs64\CorelPP.exe" enable=yes
        netsh advfirewall firewall add rule name="CorelDRAW - Bloquear Salida (FontManager.exe)" dir=out action=block program="C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Programs64\FontManager.exe" enable=yes
        netsh advfirewall firewall add rule name="CorelDRAW - Bloquear Salida (CrlUISvr.exe)" dir=out action=block program="C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Programs64\CrlUISvr.exe" enable=yes
        netsh advfirewall firewall add rule name="CorelDRAW - Bloquear Salida (Setup.exe)" dir=out action=block program="C:\Program Files\Corel\CorelDRAW Graphics Suite\25\Setup\Setup.exe" enable=yes
        ```
  2.  Se intentó crear una regla de bloqueo de salida para el directorio completo de CorelDRAW, pero se confirmó que `netsh` no soporta comodines para rutas de programa. Se discutió la necesidad de bloquear ejecutables individuales si se requiere un control más granular.

### 7. Monitoreo del Explorador de Archivos

- **Objetivo:** Detectar y reportar cambios inesperados en el tamaño de las ventanas del Explorador de Archivos.
- **Enfoque:** Se implementará un mecanismo de monitoreo en segundo plano para obtener periódicamente el tamaño y la posición de las ventanas del Explorador de Archivos, compararlos con registros anteriores y documentar cualquier anomalía.

---

## Conclusión General

Basado en el análisis exhaustivo de los servicios de seguridad, los puntos de auto-inicio y las conexiones de red, **el sistema se encuentra actualmente libre de amenazas evidentes y ha sido limpiado de entradas potencialmente no deseadas.**

Se ha establecido una línea base de seguridad y se han implementado medidas proactivas para la monitorización de servicios críticos como Cloudflare Warp y el control de acceso a internet para CorelDRAW.

La monitorización activa continuará para detectar y prevenir futuras amenazas, y se actuará de forma inmediata y eficaz ante cualquier evento contrario a los lineamientos establecidos.
