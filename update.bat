@echo off
setlocal
cd /d "%~dp0"
echo Menunggu proses aplikasi ditutup untuk memulai pembaruan...
timeout /t 2 /nobreak >nul

set "KIPAPP_BASE=%CD%"
set "KIPAPP_ZIP_URL=https://github.com/tiomultazem/kipapp-helper-v3/archive/refs/heads/main.zip"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $base=$env:KIPAPP_BASE; $url=$env:KIPAPP_ZIP_URL; $work=Join-Path $env:TEMP ('kipapp_update_' + [guid]::NewGuid()); $zip=Join-Path $work 'update.zip'; $extract=Join-Path $work 'extract'; New-Item -ItemType Directory -Force -Path $extract | Out-Null; Write-Host 'Download update...'; Invoke-WebRequest -Uri $url -OutFile $zip; Write-Host 'Unzip update...'; Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force; $src=Get-ChildItem -LiteralPath $extract -Directory | Select-Object -First 1; if(-not $src -or -not(Test-Path (Join-Path $src.FullName 'main.py'))){ throw 'ZIP update tidak valid.' }; Write-Host 'Replace file aplikasi...'; robocopy $src.FullName $base /MIR /NFL /NDL /NJH /NJS /NC /NS; if($LASTEXITCODE -gt 7){ exit $LASTEXITCODE }; Remove-Item -LiteralPath $work -Recurse -Force; Write-Host 'Menjalankan ulang aplikasi...'; Start-Process -FilePath 'python' -ArgumentList 'main.py' -WorkingDirectory $base; exit 0"
exit
