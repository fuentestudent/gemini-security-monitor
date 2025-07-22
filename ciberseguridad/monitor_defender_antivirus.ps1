$serviceName = "WinDefend"
$service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue

if ($service -eq $null) {
    Write-Host "El servicio '$serviceName' no se encontró en el sistema."
} elseif ($service.Status -ne "Running") {
    Write-Host "El servicio '$serviceName' está detenido. Intentando iniciarlo..."

    # --- Nuevo código para buscar en el registro de eventos y registrar ---
    $logEntry = Get-WinEvent -LogName System -FilterXPath "*[System[(EventID=7036 or EventID=7040) and TimeCreated[system:TimeCreated > (Get-Date).AddMinutes(-5)]]]" |
                Where-Object { $_.Message -like "*$serviceName*stopped*" -or $_.Message -like "*$serviceName*changed to disabled*" } |
                Select-Object TimeCreated, Id, LevelDisplayName, Message, @{Name='User';Expression={$_.Properties[1].Value}}, @{Name='Process';Expression={$_.Properties[0].Value}} -First 1

    if ($logEntry) {
        Write-Host "Posible causa de detención de '$serviceName' (últimos 5 minutos):"
        Write-Host "  Hora: $($logEntry.TimeCreated)"
        Write-Host "  ID de Evento: $($logEntry.Id)"
        Write-Host "  Nivel: $($logEntry.LevelDisplayName)"
        Write-Host "  Mensaje: $($logEntry.Message)"
        Write-Host "  Usuario (si disponible): $($logEntry.User)"
        Write-Host "  Proceso (si disponible): $($logEntry.Process)"
        # Log this information to a file for persistence
        Add-Content -Path "C:\www\ciberseguridad\service_monitor_log.txt" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - DETECCIÓN DE SERVICIO DETENIDO: $serviceName. Detalles del evento: $($logEntry | ConvertTo-Json -Compress)"
    } else {
        Write-Host "No se encontraron eventos recientes de detención para '$serviceName' en los últimos 5 minutos."
        Add-Content -Path "C:\www\ciberseguridad\service_monitor_log.txt" -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - DETECCIÓN DE SERVICIO DETENIDO: $serviceName. No se encontraron eventos recientes de detención."
    }
    # --- Fin del nuevo código --- 

    try {
        Start-Service -Name $serviceName -ErrorAction Stop
        Write-Host "El servicio '$serviceName' se ha iniciado correctamente."
    } catch {
        Write-Error "No se pudo iniciar el servicio '$serviceName'. Error: $($_.Exception.Message)"
    }
} else {
    Write-Host "El servicio '$serviceName' ya está en ejecución."
}