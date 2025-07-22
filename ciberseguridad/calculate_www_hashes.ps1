
$targetDirectory = "C:\www"
$outputFile = "C:\www\ciberseguridad\www_hashes.json"

$hashList = @()

Get-ChildItem -Path $targetDirectory -Recurse -File | ForEach-Object {
    $filePath = $_.FullName
    try {
        $hash = (Get-FileHash -Path $filePath -Algorithm SHA256).Hash
        $hashList += [PSCustomObject]@{ Path = $filePath; Hash = $hash }
    } catch {
        Write-Warning "No se pudo calcular el hash para $($filePath): $($_.Exception.Message)"
    }
}

$hashList | ConvertTo-Json -Depth 100 | Set-Content -Path $outputFile

Write-Host "Hashes calculados y guardados en $outputFile"
