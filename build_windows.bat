@echo off
py -m pip install pyinstaller
py -m PyInstaller --onedir --windowed --noupx --name "IP Configuration Tool" ^
  --icon "assets\feather.ico" ^
  --hidden-import=ping_monitor ^
  --hidden-import=ping_monitor_ui ^
  --add-data "ping_devices.json;." ^
  --add-data "config.json;." ^
  --add-data "assets\feather.ico;assets" ^
  main.py
if errorlevel 1 (
  echo Build failed. Check that PyInstaller installed successfully.
  pause
  exit /b 1
)
echo.
echo Build complete: dist\IP Configuration Tool\IP Configuration Tool.exe
echo Ship the whole "IP Configuration Tool" folder (zip it), not just the .exe.
pause