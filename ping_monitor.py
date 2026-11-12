import json
import os
import re
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from ping_monitor_ui import PingMonitorUI


if getattr(sys, "frozen", False):
    BASE = Path(sys.executable).resolve().parent
    RESOURCE_DIR = Path(
        getattr(sys, "_MEIPASS", BASE)
    )
    DATA_DIR = (
        Path(os.environ.get("LOCALAPPDATA", BASE))
        / "IPConfigurationTool"
    )
else:
    BASE = Path(__file__).resolve().parent
    RESOURCE_DIR = BASE
    DATA_DIR = BASE

PING_CONFIG_FILE = DATA_DIR / "ping_devices.json"
PING_SEED_FILE = RESOURCE_DIR / "ping_devices.json"


class PingMonitor:

    def __init__(self, parent):

        self.parent = parent

        # -------------------------
        # Window
        # -------------------------

        self.window = tk.Toplevel(parent)

        self.window.title("Ping Monitor")

        self.window.geometry("900x560")

        self.window.minsize(900, 560)

        # -------------------------
        # Monitoring state
        # -------------------------

        self.devices = []

        self.running = False

        self.stop_event = threading.Event()

        self.thread = None

        self.rows = {}

        self.selected_group = "All Groups"

        # -------------------------
        # Device metadata
        # -------------------------

        self.device_groups = {}

        # Cache the detected network type for each IP.
        self.network_cache = {}

        # Cache the detected MAC address for each IP.
        self.mac_cache = {}

        # -------------------------
        # Build UI
        # -------------------------

        self.ui = PingMonitorUI(self)

        # -------------------------
        # Load devices
        # -------------------------

        self.load_devices()

        # -------------------------
        # Window close
        # -------------------------

        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

    # =========================================================
    # Load Devices
    # =========================================================

    def load_devices(self):

        if not PING_CONFIG_FILE.exists():

            try:
                DATA_DIR.mkdir(
                    parents=True,
                    exist_ok=True
                )

                seed = None

                if PING_SEED_FILE.exists():
                    seed = PING_SEED_FILE.read_text(
                        encoding="utf-8"
                    )

                PING_CONFIG_FILE.write_text(
                    seed
                    or json.dumps({
                        "devices": []
                    }, indent=4),
                    encoding="utf-8"
                )

            except OSError as error:

                messagebox.showerror(
                    "Ping Monitor",
                    f"Unable to create ping_devices.json.\n\n"
                    f"{error}",
                    parent=self.window
                )

                return

        try:

            with open(
                PING_CONFIG_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            self.devices = data.get(
                "devices",
                []
            )

            # Clear existing rows

            self.ui.tree.delete(
                *self.ui.tree.get_children()
            )

            self.rows.clear()

            # Add devices

            for device in self.devices:

                name = device.get(
                    "name",
                    "Unknown"
                )

                ip = device.get(
                    "ip",
                    ""
                )

                group = device.get(
                    "group",
                    "Other"
                )

                self.device_groups[ip] = group

                item = self.ui.add_device_row(
                    name,
                    ip,
                    group
                )

                self.rows[ip] = item

            self.ui.set_groups(self.get_groups())
            self.update_summary()

        except json.JSONDecodeError:

            messagebox.showerror(
                "Ping Monitor",
                "ping_devices.json contains invalid JSON.",
                parent=self.window
            )

        except Exception as error:

            messagebox.showerror(
                "Ping Monitor",
                f"Unable to load ping_devices.json.\n\n"
                f"{error}",
                parent=self.window
            )

    # =========================================================
    # Start Ping
    # =========================================================

    def start_ping(self):

        if self.running:

            return

        if not self.devices:

            messagebox.showwarning(
                "Ping Monitor",
                "No devices are configured in "
                "ping_devices.json.",
                parent=self.window
            )

            return

        self.running = True

        self.stop_event.clear()

        self.ui.set_polling_state(
            True
        )

        self.thread = threading.Thread(
            target=self.ping_loop,
            daemon=True
        )

        self.thread.start()

    # =========================================================
    # Stop Ping
    # =========================================================

    def stop_ping(self):

        self.running = False

        self.stop_event.set()

        if hasattr(self, "ui"):

            self.ui.set_polling_state(
                False
            )

    # =========================================================
    # Manual Refresh
    # =========================================================

    def refresh_now(self):

        if getattr(self, "running", False):
            return

        if not self.devices:
            return

        if hasattr(self, "ui") and hasattr(self.ui, "refresh_button"):
            self.ui.refresh_button.config(
                state="disabled",
                text="Refreshing..."
            )
            self.ui.refresh_button.update_idletasks()

        try:
            network_cache = getattr(self, "network_cache", {})
            devices_to_ping = self.get_devices_to_ping()

            for device in devices_to_ping:

                name = device.get(
                    "name",
                    "Unknown"
                )

                ip = device.get(
                    "ip",
                    ""
                )

                if not ip:
                    continue

                result = self.ping_device(ip)
                result["group"] = self.device_groups.get(ip, "Other")
                result["network"] = network_cache.get(ip, "Unknown")

                self.window.after(
                    0,
                    self.update_row,
                    ip,
                    name,
                    result
                )

            if hasattr(self, "window"):
                self.window.after(
                    0,
                    self.update_last_cycle
                )

        finally:
            if hasattr(self, "ui") and hasattr(self.ui, "refresh_button"):
                self.ui.refresh_button.config(
                    state="normal",
                    text="↻ Refresh"
                )

    # =========================================================
    # Continuous Ping Loop
    # =========================================================

    def ping_loop(self):

        while self.running and not self.stop_event.is_set():

            devices_to_ping = self.get_devices_to_ping()

            for device in devices_to_ping:

                if not self.running or self.stop_event.is_set():

                    break

                name = device.get(
                    "name",
                    "Unknown"
                )

                ip = device.get(
                    "ip",
                    ""
                )

                result = self.ping_device(
                    ip
                )

                # Keep the ping loop lightweight. Network and MAC
                # detection are intentionally not run here because
                # they add extra Windows calls and slow down each
                # refresh cycle. These checks are available on demand
                # via the dedicated UI actions.

                result["group"] = self.device_groups.get(
                    ip,
                    "Other"
                )

                result["network"] = self.network_cache.get(
                    ip,
                    "Unknown"
                )

                self.window.after(
                    0,
                    self.update_row,
                    ip,
                    name,
                    result
                )

            if self.running and not self.stop_event.is_set():

                self.window.after(
                    0,
                    self.update_last_cycle
                )

                # Keep the loop continuous but lighter. This avoids
                # hammering all devices with a very short timeout on
                # every cycle while still polling until Stop is pressed.

                self.stop_event.wait(
                    1.5
                )

    # =========================================================
    # Ping Device
    # =========================================================

    def ping_device(
        self,
        ip
    ):

        try:

            result = subprocess.run(
                [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    "500",
                    ip
                ],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="ignore"
            )

            output = result.stdout

            # -------------------------
            # Ping failed
            # -------------------------

            if result.returncode != 0:

                return {
                    "reachable": False,
                    "bytes": "—",
                    "time": "—"
                }

            # -------------------------
            # Get bytes
            # -------------------------

            bytes_match = re.search(
                r"(?:bytes[=<>]|size[=])\s*(\d+)",
                output,
                re.IGNORECASE
            )

            # -------------------------
            # Get response time
            # -------------------------

            time_match = re.search(
                r"time[=<]\s*(\d+)\s*ms",
                output,
                re.IGNORECASE
            )

            packet_bytes = (
                bytes_match.group(1)
                if bytes_match
                else "—"
            )

            response_time = (
                f"{time_match.group(1)} ms"
                if time_match
                else "—"
            )

            return {
                "reachable": True,
                "bytes": packet_bytes,
                "time": response_time
            }

        except Exception:

            return {
                "reachable": False,
                "bytes": "—",
                "time": "—"
            }

    # =========================================================
    # Detect Network Type
    # =========================================================

    def get_network_type(self, ip):
        """
        Detect whether Windows routes traffic to the given IP
        through Wi-Fi or Ethernet.

        The result is cached so the route does not need to be
        detected again for every ping cycle.
        """

        if ip in self.network_cache:
            return self.network_cache[ip]

        try:
            # First find the interface index Windows uses for
            # this exact destination IP.
            command = [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    f"$r = Get-NetRoute -DestinationPrefix "
                    f"'{ip}/32' -ErrorAction SilentlyContinue | "
                    f"Where-Object {{$_.NextHop -ne '0.0.0.0'}} | "
                    f"Sort-Object RouteMetric,Metric | "
                    f"Select-Object -First 1; "
                    f"if ($r) {{ $r.InterfaceIndex }}"
                )
            ]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            interface_index = result.stdout.strip()

            # If there is no exact /32 route, let Windows choose
            # the best route for the destination.
            if not interface_index:
                command = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        f"$r = Get-NetRoute -DestinationPrefix "
                        f"'0.0.0.0/0' -ErrorAction SilentlyContinue | "
                        f"Sort-Object RouteMetric,Metric | "
                        f"Select-Object -First 1; "
                        f"if ($r) {{ $r.InterfaceIndex }}"
                    )
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )

                interface_index = result.stdout.strip()

            if interface_index:
                command = [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        f"(Get-NetAdapter -InterfaceIndex "
                        f"{interface_index} "
                        f"-ErrorAction SilentlyContinue).Name"
                    )
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )

                adapter_name = result.stdout.strip().lower()

                if "wi-fi" in adapter_name or "wifi" in adapter_name:
                    network_type = "Wi-Fi"
                elif "ethernet" in adapter_name:
                    network_type = "Ethernet"
                else:
                    network_type = adapter_name.title() if adapter_name else "Unknown"

            else:
                network_type = "Unknown"

        except Exception:
            network_type = "Unknown"

        self.network_cache[ip] = network_type

        return network_type

    # =========================================================
    # Detect MAC Address
    # =========================================================

    def get_mac_address(self, ip):
        """
        Read the MAC address for the destination IP from the
        Windows ARP table.

        This normally works when the destination is on the
        same local network. For routed/remote destinations,
        Windows may not expose the destination device's MAC.
        """

        try:
            # Ping first so Windows has a chance to populate
            # its ARP cache.
            subprocess.run(
                [
                    "ping",
                    "-n",
                    "1",
                    "-w",
                    "500",
                    ip
                ],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="ignore"
            )

            result = subprocess.run(
                [
                    "arp",
                    "-a",
                    ip
                ],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="ignore"
            )

            output = result.stdout

            # Windows commonly returns:
            # 192.168.1.10    00-11-22-33-44-55    dynamic
            mac_match = re.search(
                r"\b([0-9A-Fa-f]{2}(?:-[0-9A-Fa-f]{2}){5})\b",
                output
            )

            if not mac_match:
                # Also support colon-separated MAC formats.
                mac_match = re.search(
                    r"\b([0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5})\b",
                    output
                )

            if mac_match:
                mac = mac_match.group(1).upper()

                self.mac_cache[ip] = mac

                return mac

            # Keep the last known MAC if it was previously found.
            return self.mac_cache.get(
                ip,
                "—"
            )

        except Exception:
            return self.mac_cache.get(
                ip,
                "—"
            )

    # =========================================================
    # Fetch Selected Device MAC Address
    # =========================================================

    def fetch_selected_mac(self):

        if not hasattr(self, "ui"):
            return

        selection = self.ui.tree.selection()

        if not selection:
            messagebox.showwarning(
                "Ping Monitor",
                "Select a device first to fetch its MAC address.",
                parent=self.window
            )
            return

        item = selection[0]
        values = self.ui.tree.item(item, "values")

        if len(values) < 2:
            return

        ip = values[1]
        mac = self.get_mac_address(ip)

        current = self.ui.tree.item(item, "values")
        self.ui.update_device_row(
            item,
            current[0],
            current[1],
            current[5],
            current[6],
            current[7],
            current[8],
            group=current[2],
            network=current[3],
            mac=mac
        )

    # =========================================================
    # Get Device Group
    # =========================================================

    def get_device_group(self, ip):
        return self.device_groups.get(
            ip,
            "Other"
        )

    # =========================================================
    # Get Available Groups
    # =========================================================

    def get_groups(self):
        groups = {
            self.device_groups.get(ip, "Other")
            for ip in self.rows
        }

        return sorted(groups)

    # =========================================================
    # Devices to Ping
    # =========================================================

    def get_devices_to_ping(self):

        selected_group = getattr(self, "selected_group", "All Groups")
        device_groups = getattr(self, "device_groups", {})

        if selected_group == "All Groups":
            return self.devices

        return [
            device for device in self.devices
            if device_groups.get(
                device.get("ip", ""),
                "Other"
            ) == selected_group
        ]

    # =========================================================
    # Filter by Group
    # =========================================================

    def filter_group(self, group):

        self.selected_group = group

        all_items = list(self.rows.values())

        if group == "All Groups":
            for item in all_items:
                self.ui.show_group(item, True)
        else:
            for item in all_items:
                values = self.ui.tree.item(item, "values")
                row_group = values[2] if len(values) > 2 else "Other"
                self.ui.show_group(item, row_group == group)

        self.update_summary()

    # =========================================================
    # Update Row
    # =========================================================

    def update_row(
        self,
        ip,
        name,
        result
    ):

        if ip not in self.rows:

            return

        item = self.rows[ip]

        if result["reachable"]:

            status = "Reachable"

        else:

            status = "Not Reachable"

        device_groups = getattr(self, "device_groups", {})
        network_cache = getattr(self, "network_cache", {})
        mac_cache = getattr(self, "mac_cache", {})
        group = result.get("group", device_groups.get(ip, "Other"))
        network = result.get("network", network_cache.get(ip, "Unknown"))
        mac = result.get("mac", mac_cache.get(ip, "—"))
        last_check = self.current_time()

        self.ui.update_device_row(
            item,
            name,
            ip,
            status,
            result["bytes"],
            result["time"],
            last_check,
            group=group,
            network=network,
            mac=mac
        )

        self.update_summary()

    # =========================================================
    # Update Summary
    # =========================================================

    def update_summary(self):

        total = len(
            self.ui.tree.get_children()
        )

        reachable = 0

        offline = 0

        for item in self.ui.tree.get_children():

            values = self.ui.tree.item(
                item,
                "values"
            )

            if len(values) < 6:

                continue

            status = values[5]

            if status == "Reachable":

                reachable += 1

            elif status == "Not Reachable":

                offline += 1

        self.ui.update_summary(
            total,
            reachable,
            offline
        )

    # =========================================================
    # Last Cycle
    # =========================================================

    def update_last_cycle(self):

        self.ui.set_last_cycle(
            self.current_time()
        )

    # =========================================================
    # Current Time
    # =========================================================

    @staticmethod
    def current_time():

        from datetime import datetime

        return datetime.now().strftime(
            "%H:%M:%S"
        )

    # =========================================================
    # Close
    # =========================================================

    def close(self):

        self.stop_ping()

        self.window.destroy()


# =============================================================
# Standalone Test
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    root.withdraw()

    PingMonitor(root)

    root.mainloop()