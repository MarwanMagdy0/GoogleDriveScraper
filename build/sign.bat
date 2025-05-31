"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe" sign ^
    /f "build\QuickSpace.pfx" ^
    /p QuickSpace@2025 ^
    /fd SHA256 ^
    /td SHA256 ^
    /tr http://timestamp.digicert.com ^
    /v "main.dist\main.exe"
pause
