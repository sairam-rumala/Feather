# IP Configuration Tool — AI Project Context

## Goal
Build a Windows `.exe` tool to configure a device's network IP directly without using `ncpa.cpl`.

## Core Features
- Support Ethernet and Wi-Fi.
- Select network type.
- Show connection status and current IP.
- Select predefined configurations.
- Configuration names are fully user-defined.
- Configuration data stored in JSON.
- Add, edit, and delete configurations from the GUI.
- Each configuration contains:
  - Name
  - Network type
  - IP address
  - Subnet
  - Gateway
  - Optional port
- Apply static IP configuration directly through Windows networking.
- Set selected adapter back to DHCP.
- Ping configured IPs.
- Verify IP configuration after changes.
- Show success/failure status.
- Confirm before changing an existing IP.
- Validate configuration values.
- Refresh network status.
- Keep a simple activity log.
- Detect if the selected configuration is already active.
- Require/handle administrator privileges.

## Port
- Port is optional.
- Blank port must not prevent the IP configuration from working.
- Port is an associated configuration value, not a network-adapter setting.

## UI Flow
1. Open application.
2. Select Ethernet or Wi-Fi.
3. Show connection status and current IP.
4. Select a configuration.
5. Show target IP details.
6. Optionally Ping.
7. Apply configuration or switch to DHCP.
8. Verify result.
9. Show success/failure.

## Configuration Management
- Users can create configurations directly from the GUI.
- Saved configurations are written to JSON.
- Users do not need to manually edit JSON.

## Scope
- Only manage the selected device/network adapter IP configuration.
- Do not open or depend on `ncpa.cpl`.
- Do not manage unrelated network settings.

## Technology
- Language: Python
- GUI: Tkinter
- Configuration: JSON
- OS: Windows
- Network operations: Windows networking mechanisms via Python
- Ping: Windows ping via Python
- Packaging: PyInstaller
- Output: `.exe`
- Database: None
- Internet: Not required

## Current Status
Planning only. Do not implement until explicitly requested.
