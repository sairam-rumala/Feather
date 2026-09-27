@echo off
py -m pip install pyinstaller
pyinstaller --onefile --windowed --name "IP Configuration Tool" --uac-admin ^
  --hidden-import=ping_monitor ^
  --hidden-import=ping_monitor_ui ^
  --add-data "ping_devices.json;." ^
  --add-data "config.json;." ^
  main.py
pause
