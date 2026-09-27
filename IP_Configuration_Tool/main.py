import ctypes
import json
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from ui import AppUI
from ping_monitor import PingMonitor


if getattr(sys, "frozen", False):
    BASE = Path(sys.executable).resolve().parent
else:
    BASE = Path(__file__).resolve().parent

CONFIG_FILE = BASE / "config.json"


# -----------------------------
# System / Network Functions
# -----------------------------

def admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_admin():
    if admin():
        return

    params = " ".join(f'"{a}"' for a in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        None,
        1
    )
    raise SystemExit


def load_config():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(
            json.dumps({"configurations": []}, indent=2),
            encoding="utf-8"
        )

    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def run(cmd):
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        shell=True
    )


def adapter_status(adapter):
    result = run(
        f'netsh interface show interface name="{adapter}"'
    )

    return "Connected" if "Connected" in result.stdout else "Not Connected"


def current_ip(adapter):
    result = run(
        f'netsh interface ip show address name="{adapter}"'
    )

    for line in result.stdout.splitlines():
        if "IP Address" in line:
            parts = line.split(":")

            if len(parts) > 1:
                return parts[-1].strip()

    return "Unavailable"


def apply_static(adapter, config):
    ip = config["ip"]
    mask = config["subnet"]
    gateway = config["gateway"]

    command = (
        f'netsh interface ip set address '
        f'name="{adapter}" static {ip} {mask} {gateway}'
    )

    result = run(command)

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or result.stdout.strip()
            or "Unable to configure IP."
        )


def set_dhcp(adapter):
    result = run(
        f'netsh interface ip set address '
        f'name="{adapter}" source=dhcp'
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or result.stdout.strip()
            or "Unable to enable DHCP."
        )


def ping(ip):
    result = run(
        f'ping -n 1 -w 1000 {ip}'
    )

    return result.returncode == 0, result.stdout


# -----------------------------
# Application
# -----------------------------

class App:

    def __init__(self, root):
        self.root = root
        self.root.title("IP Configuration Tool")
        self.root.geometry("520x750")

        self.data = load_config()

        self.ui = AppUI(self)
        self.refresh()

    # -------------------------
    # Configuration
    # -------------------------

    def adapter(self):
        return self.network.get()

    def configs(self):
        adapter = self.adapter()

        return [
            config
            for config in self.data.get("configurations", [])
            if config.get("network") == adapter
        ]

    def selected(self):
        name = self.config.get()

        return next(
            (
                config
                for config in self.configs()
                if config.get("name") == name
            ),
            None
        )

    # -------------------------
    # UI Updates
    # -------------------------

    def refresh(self):
        adapter = self.adapter()
        status = adapter_status(adapter)

        if hasattr(self, "status"):
            self.status.config(
                text=status
            )

        if hasattr(self, "status_dot"):
            color = "#237A57" if status == "Connected" else "#A15C00"
            self.status_dot.config(fg=color)

        self.current.config(
            text=f"Current IP: {current_ip(adapter)}"
        )

        configs = self.configs()

        self.config["values"] = [
            config.get("name", "")
            for config in configs
        ]

        if configs:
            self.config.current(0)
            self.show_config()
        else:
            self.config.set("")
            self.details.config(
                text="No configurations available."
            )

        self.log_msg(
            f"Refreshed {adapter}."
        )

    def show_config(self):
        config = self.selected()

        if not config:
            return

        port = config.get("port", "")

        self.details.config(
            text=(
                f"IP Address: {config['ip']}\n"
                f"Subnet: {config['subnet']}\n"
                f"Gateway: {config['gateway']}\n"
                f"Port: {port or 'Not configured'}"
            )
        )

    # -------------------------
    # Actions
    # -------------------------

    def do_ping(self):
        config = self.selected()

        if not config:
            messagebox.showwarning(
                "Ping",
                "Select a configuration first."
            )
            return

        success, output = ping(config["ip"])

        result = "Reachable" if success else "Not reachable"

        self.log_msg(
            f"Ping {config['ip']}: {result}."
        )

        messagebox.showinfo(
            "Ping Result",
            f"{config['ip']}\n\n{result}"
        )

    def apply(self):
        config = self.selected()

        if not config:
            messagebox.showwarning(
                "Apply",
                "Select a configuration first."
            )
            return

        old_ip = current_ip(self.adapter())

        if old_ip == config["ip"]:
            messagebox.showinfo(
                "Apply",
                "This configuration is already active."
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm",
            f"Change IP from {old_ip} to {config['ip']}?"
        )

        if not confirmed:
            return

        try:
            apply_static(
                self.adapter(),
                config
            )

            new_ip = current_ip(
                self.adapter()
            )

            self.log_msg(
                f"IP changed: {old_ip} -> {config['ip']}."
            )

            messagebox.showinfo(
                "Success",
                f"Configuration applied.\n"
                f"Current IP: {new_ip}"
            )

            self.refresh()

        except Exception as error:
            self.log_msg(
                f"Apply failed: {error}"
            )

            messagebox.showerror(
                "Failed",
                str(error)
            )

    def dhcp(self):
        adapter = self.adapter()

        confirmed = messagebox.askyesno(
            "Confirm",
            f"Set {adapter} to DHCP?"
        )

        if not confirmed:
            return

        try:
            set_dhcp(adapter)

            self.log_msg(
                f"{adapter} switched to DHCP."
            )

            messagebox.showinfo(
                "Success",
                "DHCP enabled. Refresh to see the obtained IP."
            )

            self.refresh()

        except Exception as error:
            self.log_msg(
                f"DHCP failed: {error}"
            )

            messagebox.showerror(
                "Failed",
                str(error)
            )

    # -------------------------
    # Log
    # -------------------------

    def log_msg(self, message):
        self.log.config(state="normal")

        self.log.insert(
            "end",
            message + "\n"
        )

        self.log.see("end")
        self.log.config(state="disabled")

    # -------------------------
    # Ping Monitor
    # -------------------------

    def manage(self):
        PingMonitor(self.root)


# -----------------------------
# Start Application
# -----------------------------

if __name__ == "__main__":
    relaunch_admin()

    root = tk.Tk()

    App(root)

    root.mainloop()