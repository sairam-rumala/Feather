# IP Configuration Tool

Windows tool for changing Ethernet/Wi-Fi IP configuration without using `ncpa.cpl`.

## Run in VS Code
1. Install Python 3 for Windows and the Python Launcher.
2. Open this folder in VS Code.
3. In the VS Code terminal, check Python with `py --version`.
4. Run `py main.py`. Administrator rights are requested only when you apply a
   configuration or switch the adapter to DHCP.
5. Edit `config.json` with your configurations. In the built app the file lives in
   `%LOCALAPPDATA%\IPConfigurationTool` and is created on first run.

Use `py` for this project on Windows. The `python` command may resolve to a
Microsoft Store execution alias even when Python is installed. If you also
want `python` to work, turn off the `python.exe` and `python3.exe` aliases in
**Settings > Apps > Advanced app settings > App execution aliases**, make sure
your Python install is on `PATH`, and open a new terminal.

## Build EXE on Windows
Run:

```bat
build_windows.bat
```

The build produces a folder: `dist/IP Configuration Tool/`.

Ship the whole folder (zip it) — not the `.exe` on its own. The folder build
starts in about a second, while a single-file build has to unpack itself into a
temporary folder on every launch.

Settings are stored per user in `%LOCALAPPDATA%\IPConfigurationTool`
(`config.json` and `ping_devices.json`), so the app also works when it is run
from `Program Files` or any other read-only location.

## Icon
`assets/feather.ico` is the application icon (the Feather logo, MIT licensed).
The build applies it to the `.exe` and to the window title bar. Replace the file
with your own multi-size `.ico` to rebrand; keep the same name so the build
script keeps working. If Windows still shows the old icon after a rebuild, clear
the icon cache with `ie4uinit.exe -show`.

## Configuration
Each entry contains:
- `name`
- `network`
- `ip`
- `subnet`
- `gateway`
- optional `port`

Blank `port` is valid.
