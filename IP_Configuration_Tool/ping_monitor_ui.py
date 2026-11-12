import tkinter as tk
from tkinter import messagebox, ttk


# -----------------------------
# UI Colors
# -----------------------------

BG = "#F4F5F7"
WHITE = "#FFFFFF"
LIGHT = "#FAFAFB"
BORDER = "#28292B"

TEXT = "#20242A"
MUTED = "#6B7280"

PRIMARY = "#2F5BEA"
PRIMARY_HOVER = "#2449C7"

SUCCESS = "#237A57"
WARNING = "#FD0909"

INFO = "#2F5BEA"


# -----------------------------
# UI Sizes
# -----------------------------

PAGE_PADDING = 24
SECTION_GAP = 16
SMALL_GAP = 6
MEDIUM_GAP = 10


class PingMonitorUI:

    def __init__(self, monitor):
        self.monitor = monitor
        self.window = monitor.window

        self.setup_window()
        self.setup_styles()
        self.build()

    # -------------------------
    # Window
    # -------------------------

    def setup_window(self):

        self.window.configure(bg=BG)

        self.window.minsize(1100, 620)

        # Center the window on the screen
        self.center_window(1100, 620)

    def center_window(self, width, height):

        self.window.update_idletasks()

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        self.window.geometry(
            f"{width}x{height}+{x}+{y}"
        )

    # -------------------------
    # Styles
    # -------------------------

    def setup_styles(self):

        style = ttk.Style(self.window)

        style.theme_use("clam")

        # -------------------------
        # Frames
        # -------------------------

        style.configure(
            "App.TFrame",
            background=BG
        )

        style.configure(
            "Card.TFrame",
            background=WHITE,
            relief="solid",
            borderwidth=1
        )

        # -------------------------
        # Labels
        # -------------------------

        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 19, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=MUTED,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Section.TLabel",
            background=WHITE,
            foreground=TEXT,
            font=("Segoe UI", 10, "bold")
        )

        style.configure(
            "Label.TLabel",
            background=WHITE,
            foreground=TEXT,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Value.TLabel",
            background=WHITE,
            foreground=TEXT,
            font=("Segoe UI", 10)
        )

        style.configure(
            "Muted.TLabel",
            background=WHITE,
            foreground=MUTED,
            font=("Segoe UI", 9)
        )

        # -------------------------
        # Primary Button
        # -------------------------

        style.configure(
            "Primary.TButton",
            background=PRIMARY,
            foreground=WHITE,
            font=("Segoe UI", 9, "bold"),
            padding=(14, 8),
            borderwidth=0
        )

        style.map(
            "Primary.TButton",
            background=[
                ("active", PRIMARY_HOVER),
                ("pressed", PRIMARY_HOVER),
                ("disabled", "#AEB9D8")
            ],
            foreground=[
                ("disabled", "#F3F4F6")
            ]
        )

        # -------------------------
        # Secondary Button
        # -------------------------

        style.configure(
            "Secondary.TButton",
            background=WHITE,
            foreground=TEXT,
            font=("Segoe UI", 9),
            padding=(14, 8),
            borderwidth=1,
            relief="solid"
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", LIGHT),
                ("pressed", LIGHT),
                ("disabled", "#F3F4F6")
            ],
            foreground=[
                ("disabled", "#9CA3AF")
            ]
        )

        # -------------------------
        # Summary Number
        # -------------------------

        style.configure(
            "SummaryNumber.TLabel",
            background=WHITE,
            foreground=TEXT,
            font=("Segoe UI", 18, "bold")
        )

        style.configure(
            "SummaryLabel.TLabel",
            background=WHITE,
            foreground=MUTED,
            font=("Segoe UI", 9)
        )

        # -------------------------
        # Treeview
        # -------------------------

        style.configure(
            "Monitor.Treeview",
            background=WHITE,
            foreground=TEXT,
            fieldbackground=WHITE,
            font=("Segoe UI", 9),
            rowheight=36,
            borderwidth=0
        )

        style.configure(
            "Monitor.Treeview.Heading",
            background=LIGHT,
            foreground=TEXT,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=(10, 8)
        )

        style.map(
            "Monitor.Treeview",
            background=[
                ("selected", "#E8EEFF")
            ],
            foreground=[
                ("selected", TEXT)
            ]
        )

        # -------------------------
        # Scrollbar
        # -------------------------

        style.configure(
            "Monitor.Vertical.TScrollbar",
            background=LIGHT,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=MUTED
        )

    # -------------------------
    # Main UI
    # -------------------------

    def build(self):

        self.main = ttk.Frame(
            self.window,
            style="App.TFrame",
            padding=PAGE_PADDING
        )

        self.main.pack(
            fill="both",
            expand=True
        )

        self.build_header()

        self.build_summary()

        self.build_filter()

        self.build_toolbar()

        self.build_table()

        self.build_footer()

    # -------------------------
    # Header
    # -------------------------

    def build_header(self):

        header = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        header.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        # Left side

        title_frame = ttk.Frame(
            header,
            style="App.TFrame"
        )

        title_frame.pack(
            side="left"
        )

        ttk.Label(
            title_frame,
            text="Ping Monitor",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            title_frame,
            text="Configured devices · ping_devices.json",
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(3, 0)
        )

        # Right side

        monitor_badge = tk.Label(
            header,
            text="MONITOR",
            bg=BG,
            fg=PRIMARY,
            font=("Segoe UI", 9, "bold")
        )

        monitor_badge.pack(
            side="right",
            anchor="n",
            pady=(4, 0)
        )

    # -------------------------
    # Summary
    # -------------------------

    def build_summary(self):

        summary_container = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        summary_container.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        # Devices

        self.device_card = self.create_summary_card(
            summary_container,
            "0",
            "Devices"
        )

        self.device_card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8)
        )

        # Reachable

        self.reachable_card = self.create_summary_card(
            summary_container,
            "0",
            "Reachable"
        )

        self.reachable_card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        # Offline

        self.offline_card = self.create_summary_card(
            summary_container,
            "0",
            "Not Reachable"
        )

        self.offline_card.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0)
        )

    def create_summary_card(
        self,
        parent,
        number,
        label
    ):

        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        content = tk.Frame(
            card,
            bg=WHITE
        )

        content.pack(
            fill="x",
            padx=14,
            pady=11
        )

        number_label = tk.Label(
            content,
            text=number,
            bg=WHITE,
            fg=TEXT,
            font=("Segoe UI", 18, "bold")
        )

        number_label.pack(
            anchor="w"
        )

        text_label = tk.Label(
            content,
            text=label,
            bg=WHITE,
            fg=MUTED,
            font=("Segoe UI", 9)
        )

        text_label.pack(
            anchor="w",
            pady=(1, 0)
        )

        card.number_label = number_label
        card.text_label = text_label

        return card

    # -------------------------
    # Group Filter
    # -------------------------

    def build_filter(self):

        filter_frame = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        filter_frame.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        ttk.Label(
            filter_frame,
            text="Project / Group",
            style="Subtitle.TLabel"
        ).pack(
            side="left",
            padx=(0, 8)
        )

        self.group_var = tk.StringVar(
            value="All Groups"
        )

        self.group_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.group_var,
            state="readonly",
            width=22
        )

        self.group_combo.pack(
            side="left"
        )

        self.group_combo.bind(
            "<<ComboboxSelected>>",
            self.on_group_changed
        )

        self.monitor.group_filter = self.group_var
        self.monitor.group_combo = self.group_combo

    # -------------------------
    # Group Filter Change
    # -------------------------

    def on_group_changed(self, event=None):

        if getattr(self.monitor, "running", False):
            current_group = getattr(self.monitor, "selected_group", "All Groups")
            self.group_var.set(current_group)
            messagebox.showwarning(
                "Ping Monitor",
                "Stop the current scan before changing the group.",
                parent=getattr(self, "window", None)
            )
            return

        group = self.group_var.get()

        if hasattr(self.monitor, "filter_group"):
            self.monitor.filter_group(group)

    # -------------------------
    # Toolbar
    # -------------------------

    def build_toolbar(self):

        toolbar = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        toolbar.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        # Start button

        self.start_button = ttk.Button(
            toolbar,
            text="▶  Start Ping",
            style="Primary.TButton",
            command=self.monitor.start_ping
        )

        self.start_button.pack(
            side="left"
        )

        # Stop button

        self.stop_button = ttk.Button(
            toolbar,
            text="■  Stop",
            style="Secondary.TButton",
            command=self.monitor.stop_ping,
            state="disabled"
        )

        self.stop_button.pack(
            side="left",
            padx=(8, 0)
        )

        self.refresh_button = ttk.Button(
            toolbar,
            text="↻ Refresh",
            style="Secondary.TButton",
            command=self.monitor.refresh_now
        )

        self.refresh_button.pack(
            side="left",
            padx=(8, 0)
        )

        self.fetch_mac_button = ttk.Button(
            toolbar,
            text="Fetch Selected MAC",
            style="Secondary.TButton",
            command=self.monitor.fetch_selected_mac
        )

        self.fetch_mac_button.pack(
            side="left",
            padx=(8, 0)
        )

    # -------------------------
    # Table
    # -------------------------

    def build_table(self):

        table_card = tk.Frame(
            self.main,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        table_card.pack(
            fill="both",
            expand=True
        )

        table_frame = tk.Frame(
            table_card,
            bg=WHITE
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1
        )

        columns = (
            "device",
            "ip",
            "group",
            "network",
            "mac",
            "status",
            "bytes",
            "time",
            "last_check"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Monitor.Treeview",
            selectmode="browse"
        )

        # Headings

        self.tree.heading(
            "device",
            text="Device"
        )

        self.tree.heading(
            "ip",
            text="IP Address"
        )

        self.tree.heading(
            "group",
            text="Group"
        )

        self.tree.heading(
            "network",
            text="Network"
        )

        self.tree.heading(
            "mac",
            text="MAC Address"
        )

        self.tree.heading(
            "status",
            text="Status"
        )

        self.tree.heading(
            "bytes",
            text="Bytes"
        )

        self.tree.heading(
            "time",
            text="Time"
        )

        self.tree.heading(
            "last_check",
            text="Last Check"
        )

        # Columns

        self.tree.column(
            "device",
            width=180,
            minwidth=140,
            anchor="w"
        )

        self.tree.column(
            "ip",
            width=160,
            minwidth=130,
            anchor="w"
        )

        self.tree.column(
            "group",
            width=120,
            minwidth=90,
            anchor="w"
        )

        self.tree.column(
            "network",
            width=100,
            minwidth=85,
            anchor="w"
        )

        self.tree.column(
            "mac",
            width=150,
            minwidth=135,
            anchor="w"
        )

        self.tree.column(
            "status",
            width=160,
            minwidth=130,
            anchor="w"
        )

        self.tree.column(
            "bytes",
            width=90,
            minwidth=70,
            anchor="center"
        )

        self.tree.column(
            "time",
            width=100,
            minwidth=80,
            anchor="center"
        )

        self.tree.column(
            "last_check",
            width=130,
            minwidth=110,
            anchor="center"
        )

        # Scrollbar

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
            style="Monitor.Vertical.TScrollbar"
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Row tags

        self.tree.tag_configure(
            "reachable",
            foreground=SUCCESS
        )

        self.tree.tag_configure(
            "offline",
            foreground=WARNING
        )

        self.tree.tag_configure(
            "unchecked",
            foreground=MUTED
        )

        # Connect the UI tree to the monitor logic

        self.monitor.tree = self.tree

    # -------------------------
    # Footer
    # -------------------------

    def build_footer(self):

        footer = ttk.Frame(
            self.main,
            style="App.TFrame"
        )

        footer.pack(
            fill="x",
            pady=(12, 0)
        )

        self.polling_label = ttk.Label(
            footer,
            text="Polling: inactive",
            style="Subtitle.TLabel"
        )

        self.polling_label.pack(
            side="left"
        )

        self.last_cycle_label = ttk.Label(
            footer,
            text="Last cycle: --",
            style="Subtitle.TLabel"
        )

        self.last_cycle_label.pack(
            side="right"
        )

        # Give monitor.py access to these UI elements

        self.monitor.polling_label = self.polling_label
        self.monitor.last_cycle_label = self.last_cycle_label
        self.monitor.start_button = self.start_button
        self.monitor.stop_button = self.stop_button

        self.monitor.device_count_label = (
            self.device_card.number_label
        )

        self.monitor.reachable_label = (
            self.reachable_card.number_label
        )

        self.monitor.offline_label = (
            self.offline_card.number_label
        )

    # -------------------------
    # Add Device Row
    # -------------------------

    def add_device_row(
        self,
        name,
        ip,
        group="Other"
    ):

        item = self.tree.insert(
            "",
            "end",
            values=(
                name,
                ip,
                group,
                "Unknown",
                "—",
                "Not Checked",
                "—",
                "—",
                "—"
            ),
            tags=("unchecked",)
        )

        return item

    # -------------------------
    # Update Device Row
    # -------------------------

    def update_device_row(
        self,
        item,
        name,
        ip,
        status,
        packet_bytes,
        response_time,
        last_check,
        group="Other",
        network="Unknown",
        mac="—"
    ):

        if status == "Reachable":

            tag = "reachable"

        elif status == "Not Reachable":

            tag = "offline"

        else:

            tag = "unchecked"

        self.tree.item(
            item,
            values=(
                name,
                ip,
                group,
                network,
                mac,
                status,
                packet_bytes,
                response_time,
                last_check
            ),
            tags=(tag,)
        )

    # -------------------------
    # Update Group Filter
    # -------------------------

    def set_groups(self, groups):

        values = ["All Groups"] + list(groups)

        self.group_combo["values"] = values

        if self.group_var.get() not in values:
            self.group_var.set("All Groups")

    # -------------------------
    # Apply Group Filter
    # -------------------------

    def show_group(self, item, visible):

        if visible:
            self.tree.reattach(
                item,
                "",
                "end"
            )
        else:
            self.tree.detach(item)

    # -------------------------
    # Update Summary
    # -------------------------

    def update_summary(
        self,
        total,
        reachable,
        offline
    ):

        self.device_card.number_label.config(
            text=str(total)
        )

        self.reachable_card.number_label.config(
            text=str(reachable)
        )

        self.offline_card.number_label.config(
            text=str(offline)
        )

    # -------------------------
    # Polling State
    # -------------------------

    def set_polling_state(
        self,
        active
    ):

        if active:

            self.polling_label.config(
                text="Polling: active"
            )

            self.start_button.config(
                state="disabled"
            )

            self.stop_button.config(
                state="normal"
            )

            if hasattr(self, "refresh_button"):
                self.refresh_button.config(
                    state="disabled",
                    text="↻ Refresh"
                )

            if hasattr(self, "group_combo"):
                self.group_combo.config(
                    state="disabled"
                )

        else:

            self.polling_label.config(
                text="Polling: inactive"
            )

            self.start_button.config(
                state="normal"
            )

            self.stop_button.config(
                state="disabled"
            )

            if hasattr(self, "refresh_button"):
                self.refresh_button.config(
                    state="normal",
                    text="↻ Refresh"
                )

            if hasattr(self, "group_combo"):
                self.group_combo.config(
                    state="readonly"
                )

    # -------------------------
    # Last Cycle
    # -------------------------

    def set_last_cycle(
        self,
        time_value
    ):

        self.last_cycle_label.config(
            text=f"Last cycle: {time_value}"
        )