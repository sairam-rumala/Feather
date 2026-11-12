# IP Configuration Tool

Windows tool for changing Ethernet/Wi-Fi IP configuration without using `ncpa.cpl`.

## Run in VS Code
1. Install Python 3.
2. Open this folder in VS Code.
3. Run `python main.py` as Administrator.
4. Edit `config.json` with your configurations.

## Build EXE on Windows
Run:

```bat
build_windows.bat
```

The EXE will be created in `dist/IPConfigurationTool.exe`.

## Configuration
Each entry contains:
- `name`
- `network`
- `ip`
- `subnet`
- `gateway`
- optional `port`

Blank `port` is valid.
