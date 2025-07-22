$logFile = "C:\www\ciberseguridad\explorer_window_log.txt"

function Get-ExplorerWindows {
    $windows = @()
    Add-Type -AssemblyName System.Windows.Forms
    $shell = New-Object -ComObject Shell.Application
    foreach ($win in $shell.Windows()) {
        if ($win.Name -eq "Explorador de archivos") {
            $windows += [PSCustomObject]@{ 
                Title = $win.Document.Title;
                Left = $win.Left;
                Top = $win.Top;
                Width = $win.Width;
                Height = $win.Height;
                ProcessId = $win.ProcessID
            }
        }
    }
    return $windows
}

function Get-RunningProcesses {
    Get-Process | Select-Object ProcessName, Id, Path | ConvertTo-Json -Compress
}

$currentWindows = Get-ExplorerWindows
$previousWindows = Get-Content -Path $logFile -ErrorAction SilentlyContinue | ConvertFrom-Json

if ($previousWindows -eq $null) {
    $previousWindows = @()
}

$changesDetected = $false

# Check for changes in existing windows
foreach ($currentWin in $currentWindows) {
    $match = $previousWindows | Where-Object { $_.Title -eq $currentWin.Title -and $_.ProcessId -eq $currentWin.ProcessId }
    if ($match) {
        if ($match.Left -ne $currentWin.Left -or `
            $match.Top -ne $currentWin.Top -or `
            $match.Width -ne $currentWin.Width -or `
            $match.Height -ne $currentWin.Height) {
            
            $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - CAMBIO DETECTADO: Ventana ''$currentWin.Title'' (PID: $($currentWin.ProcessId)) - Tamaño/Posición anterior: (Left: $($match.Left), Top: $($match.Top), Width: $($match.Width), Height: $($match.Height)) - Nuevo: (Left: $($currentWin.Left), Top: $($currentWin.Top), Width: $($currentWin.Width), Height: $($currentWin.Height))"
            Add-Content -Path $logFile -Value $logEntry
            Add-Content -Path $logFile -Value "Procesos en ejecución al momento del cambio: $(Get-RunningProcesses)"
            $changesDetected = $true
        }
    } else {
        # New window detected
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - NUEVA VENTANA: Ventana ''$currentWin.Title'' (PID: $($currentWin.ProcessId)) - Tamaño/Posición: (Left: $($currentWin.Left), Top: $($currentWin.Top), Width: $($currentWin.Width), Height: $($currentWin.Height))"
        Add-Content -Path $logFile -Value $logEntry
        Add-Content -Path $logFile -Value "Procesos en ejecución al momento de la nueva ventana: $(Get-RunningProcesses)"
        $changesDetected = $true
    }
}

# Check for closed windows
foreach ($previousWin in $previousWindows) {
    $match = $currentWindows | Where-Object { $_.Title -eq $previousWin.Title -and $_.ProcessId -eq $previousWin.ProcessId }
    if (-not $match) {
        $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - VENTANA CERRADA: Ventana ''$previousWin.Title'' (PID: $($previousWin.ProcessId))"
        Add-Content -Path $logFile -Value $logEntry
        Add-Content -Path $logFile -Value "Procesos en ejecución al momento del cierre: $(Get-RunningProcesses)"
        $changesDetected = $true
    }
}

# Save current state for next comparison
$currentWindows | ConvertTo-Json | Set-Content -Path $logFile

if (-not $changesDetected) {
    # Optionally log no changes for debugging or detailed history
    # Add-Content -Path $logFile -Value "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - No se detectaron cambios en las ventanas del Explorador de Archivos."
}