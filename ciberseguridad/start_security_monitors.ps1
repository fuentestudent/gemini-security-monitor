# Script maestro para iniciar los monitores de seguridad

# Ejecutar el monitor de Cloudflare Warp
& "C:\www\ciberseguridad\monitor_warp.ps1"

# Ejecutar el monitor de Microsoft Defender Antivirus
& "C:\www\ciberseguridad\monitor_defender_antivirus.ps1"

# Ejecutar el monitor del Firewall de Windows Defender
& "C:\www\ciberseguridad\monitor_defender_firewall.ps1"

# Ejecutar el monitor de CrowdSec
& "C:\www\ciberseguridad\monitor_crowdsec.ps1"

# Ejecutar el monitor de ventanas del Explorador de Archivos (PowerShell)
# Si prefieres la versión en Python, puedes cambiar la línea siguiente:
# & "C:\www\ciberseguridad\monitor_explorer_windows.py"
& "C:\www\ciberseguridad\monitor_explorer_windows.ps1"

# Ejecutar escaneo de Windows Defender en C:\www
Write-Host "Iniciando escaneo de Windows Defender en C:\www..."
Start-Process -FilePath "C:\Program Files\Windows Defender\MpCmdRun.exe" -ArgumentList "-Scan -ScanType 3 -File C:\www -DisableRemediation" -NoNewWindow -Wait
Write-Host "Escaneo de Windows Defender completado."

# Ejecutar verificación de integridad del directorio C:\www
Write-Host "Iniciando verificación de integridad del directorio C:\www..."
& "C:\www\ciberseguridad\verify_www_integrity.ps1"
Write-Host "Verificación de integridad completada."
