import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from ui import AppUI
from ping_monitor import PingMonitor


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

CONFIG_FILE = DATA_DIR / "config.json"
SEED_CONFIG_FILE = RESOURCE_DIR / "config.json"

ICON_FILE = RESOURCE_DIR / "assets" / "feather.ico"

# Arguments used when the tool restarts itself with administrator
# rights to perform a single change.
APPLY_FLAG = "--apply-static"
DHCP_FLAG = "--set-dhcp"
ADAPTER_FLAG = "--adapter"


# -----------------------------
# System / Network Functions
# -----------------------------

def admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def quote(value):
    return f'"{value}"'


def set_icon(window):
    try:
        if ICON_FILE.exists():
            window.iconbitmap(str(ICON_FILE))

    except Exception:
        pass


def launch_params(args):
    values = []

    if not getattr(sys, "frozen", False):
        values.append(str(Path(__file__).resolve()))

    values.extend(args)

    return " ".join(quote(value) for value in values)


def admin_request(argv):
    """Return (mode, values) when this process was started to
    perform a single administrator task."""

    if DHCP_FLAG in argv:
        index = argv.index(DHCP_FLAG)

        if index + 1 >= len(argv):
            return None, None

        return "dhcp", [argv[index + 1]]

    if APPLY_FLAG in argv:
        index = argv.index(APPLY_FLAG)

        values = argv[index + 1:index + 4]

        if len(values) < 3:
            return None, None

        adapter = "Ethernet"

        if ADAPTER_FLAG in argv:
            adapter_index = argv.index(ADAPTER_FLAG)

            if adapter_index + 1 < len(argv):
                adapter = argv[adapter_index + 1]

        return "apply", values + [adapter]

    return None, None


def perform_task(mode, values):
    root = tk.Tk()

    root.withdraw()

    try:
        if mode == "dhcp":
            set_dhcp(values[0])

            summary = f"{values[0]} switched to DHCP."

        else:
            ip, subnet, gateway, adapter = values

            previous = current_ip(adapter)

            apply_static(
                adapter,
                {
                    "ip": ip,
                    "subnet": subnet,
                    "gateway": gateway
                }
            )

            summary = (
                f"Configuration applied.\n"
                f"IP: {ip}\n"
                f"Previous IP: {previous}"
            )

        messagebox.showinfo(
            "Success",
            summary
        )

    except Exception as error:
        messagebox.showerror(
            "Failed",
            str(error)
        )

    finally:
        root.destroy()


def load_config():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        seed = read_seed(SEED_CONFIG_FILE)

        CONFIG_FILE.write_text(
            seed
            or json.dumps({"configurations": []}, indent=2),
            encoding="utf-8"
        )

    return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))


def read_seed(path):
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except OSError:
        pass

    return None


def run(cmd, timeout=15):
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        errors="ignore",
        shell=True,
        timeout=timeout
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

        set_icon(self.root)

        self.data = load_config()

        self.refresh_token = 0

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

        self.refresh_status()

    def refresh_status(self):
        adapter = self.adapter()

        self.refresh_token += 1

        token = self.refresh_token

        def worker():
            try:
                status = adapter_status(adapter)
                ip = current_ip(adapter)
            except Exception:
                return

            try:
                self.root.after(
                    0,
                    self.apply_status,
                    token,
                    adapter,
                    status,
                    ip
                )
            except Exception:
                pass

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def apply_status(self, token, adapter, status, ip):
        if token != self.refresh_token:
            return

        if self.adapter() != adapter:
            return

        if hasattr(self, "status"):
            self.status.config(
                text=status
            )

        if hasattr(self, "status_dot"):
            color = "#237A57" if status == "Connected" else "#A15C00"
            self.status_dot.config(fg=color)

        self.current.config(
            text=f"Current IP: {ip}"
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

        if not admin():
            self.request_change(
                [
                    APPLY_FLAG,
                    config["ip"],
                    config["subnet"],
                    config["gateway"],
                    ADAPTER_FLAG,
                    self.adapter()
                ],
                self.adapter(),
                config["ip"]
            )

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

        if not admin():
            self.request_change(
                [DHCP_FLAG, adapter],
                adapter,
                None
            )

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

    def request_change(self, args, adapter, target):
        result = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            sys.executable,
            launch_params(args),
            None,
            1
        )

        if result <= 32:
            messagebox.showerror(
                "Administrator required",
                "Windows could not restart the tool with "
                "administrator rights."
            )

            return

        self.log_msg(
            "Waiting for administrator approval..."
        )

        self.wait_for_change(
            adapter,
            target
        )

    def wait_for_change(self, adapter, target, timeout=20):
        def worker():
            changed = False

            deadline = time.time() + timeout

            while time.time() < deadline:

                time.sleep(0.5)

                if target is None:
                    time.sleep(1.5)

                    changed = True

                    break

                try:
                    if current_ip(adapter) == target:
                        changed = True

                        break

                except Exception:
                    pass

            try:
                self.root.after(
                    0,
                    self.finish_change,
                    adapter,
                    target,
                    changed
                )

            except Exception:
                pass

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def finish_change(self, adapter, target, changed):
        if changed:
            if target is None:
                self.log_msg(
                    f"{adapter} switched to DHCP."
                )

            else:
                self.log_msg(
                    f"IP changed to {target}."
                )

        else:
            self.log_msg(
                "Change was not completed."
            )

        self.refresh()

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
    mode, values = admin_request(sys.argv[1:])

    if mode:
        perform_task(mode, values)

        raise SystemExit

    root = tk.Tk()

    App(root)

    root.mainloop()