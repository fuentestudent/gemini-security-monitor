
$backupDir = "C:\www\ciberseguridad\event_logs_backup"
$integrityLog = "C:\www\ciberseguridad\event_logs_integrity.log"
$date = Get-Date -Format "yyyyMMdd_HHmmss"

$logNames = @("System", "Security", "Application")

foreach ($logName in $logNames) {
    $outputPath = Join-Path $backupDir "$($logName)_$($date).evtx"
    try {
        # Exportar el registro de eventos
        Get-WinEvent -LogName $logName -ErrorAction Stop | Export-WinEvent -Path $outputPath -ErrorAction Stop
        Write-Host "Registro de eventos '$logName' exportado a $outputPath"

        # Calcular el hash del archivo exportado
        $hash = (Get-FileHash -Path $outputPath -Algorithm SHA256).Hash
        Write-Host "Hash SHA256 de '$logName' exportado: $hash"

        # Registrar en el log de integridad
        Add-Content -Path $integrityLog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - BACKUP_EVENT_LOG: LogName=$logName, Path=$outputPath, Hash=$hash"

    } catch {
        Write-Error "Error al exportar o hashear el registro de eventos '$logName': $($_.Exception.Message)"
        Add-Content -Path $integrityLog -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ERROR_BACKUP_EVENT_LOG: LogName=$logName, Error=$($_.Exception.Message)"
    }
}
