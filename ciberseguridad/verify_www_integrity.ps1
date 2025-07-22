
$targetDirectory = "C:\www"
$referenceFile = "C:\www\ciberseguridad\www_hashes.json"
$logFile = "C:\www\ciberseguridad\integrity_check_log.txt"

# Cargar hashes de referencia
$referenceHashes = @{}
if (Test-Path $referenceFile) {
    (Get-Content $referenceFile | ConvertFrom-Json) | ForEach-Object {
        $referenceHashes[$_.Path] = $_.Hash
    }
} else {
    Write-Warning "Archivo de hashes de referencia no encontrado: $referenceFile. Ejecute calculate_www_hashes.ps1 primero."
    exit
}

$currentFiles = @{}
Get-ChildItem -Path $targetDirectory -Recurse -File | ForEach-Object {
    $currentFiles[$_.FullName] = $true
}

$changesDetected = $false

# Verificar archivos existentes y detectar nuevos
Get-ChildItem -Path $targetDirectory -Recurse -File | ForEach-Object {
    $filePath = $_.FullName
    try {
        $currentHash = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
        if ($referenceHashes.ContainsKey($filePath)) {
            if ($referenceHashes[$filePath] -ne $currentHash) {
                $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ARCHIVO MODIFICADO: $filePath (Hash anterior: $($referenceHashes[$filePath]), Hash actual: $currentHash)"
                Add-Content -Path $logFile -Value $logMessage
                Write-Host $logMessage
                $changesDetected = $true
            }
        } else {
            $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ARCHIVO NUEVO DETECTADO: $filePath (Hash: $currentHash)"
            Add-Content -Path $logFile -Value $logMessage
            Write-Host $logMessage
            $changesDetected = $true
        }
    } catch {
        Write-Warning "No se pudo calcular el hash para $($filePath): $($_.Exception.Message)"
    }
}

# Detectar archivos eliminados
foreach ($refPath in $referenceHashes.Keys) {
    if (-not $currentFiles.ContainsKey($refPath)) {
        $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - ARCHIVO ELIMINADO: $refPath"
        Add-Content -Path $logFile -Value $logMessage
        Write-Host $logMessage
        $changesDetected = $true
    }
}

if (-not $changesDetected) {
    $logMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - Verificación de integridad completada: No se detectaron cambios en C:\www."
    Add-Content -Path $logFile -Value $logMessage
    Write-Host $logMessage
}
