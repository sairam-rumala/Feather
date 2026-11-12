import tkinter as tk
from tkinter import ttk


# -----------------------------
# UI Colors
# -----------------------------

BG = "#F4F5F7"
WHITE = "#FFFFFF"
LIGHT = "#FAFAFB"
BORDER = "#E1E4E8"

TEXT = "#20242A"
MUTED = "#6B7280"

PRIMARY = "#2F5BEA"
PRIMARY_HOVER = "#2449C7"

SUCCESS = "#237A57"
WARNING = "#FD0909"


# -----------------------------
# UI Sizes
# -----------------------------

PAGE_PADDING = 24
SECTION_GAP = 16
SMALL_GAP = 6
MEDIUM_GAP = 10


class AppUI:

    def __init__(self, app):
        self.app = app
        self.root = app.root

        self.setup_window()
        self.setup_styles()
        self.build()

    # -------------------------
    # Window
    # -------------------------

    def setup_window(self):
        self.root.configure(bg=BG)

        self.root.minsize(520, 750)

    # -------------------------
    # Styles
    # -------------------------

    def setup_styles(self):

        style = ttk.Style(self.root)

        style.theme_use("clam")

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

        style.configure(
            "Title.TLabel",
            background=BG,
            foreground=TEXT,
            font=("Segoe UI", 19, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=TEXT,
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
            "Status.TLabel",
            background=WHITE,
            foreground=SUCCESS,
            font=("Segoe UI", 9, "bold")
        )

        style.configure(
            "TCombobox",
            fieldbackground=WHITE,
            background=WHITE,
            foreground=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=7
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", WHITE)
            ],
            selectbackground=[
                ("readonly", WHITE)
            ],
            selectforeground=[
                ("readonly", TEXT)
            ]
        )

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
                ("pressed", PRIMARY_HOVER)
            ]
        )

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
                ("active", LIGHT)
            ]
        )

    # -------------------------
    # Main UI
    # -------------------------

    def build(self):

        self.main = ttk.Frame(
            self.root,
            style="App.TFrame",
            padding=PAGE_PADDING
        )

        self.main.pack(
            fill="both",
            expand=True
        )

        self.build_header()
        self.build_network_section()
        self.build_configuration_section()
        self.build_actions_section()
        self.build_log_section()
        self.build_footer()

    # -------------------------
    # Header
    # -------------------------

    def build_header(self):

        ttk.Label(
            self.main,
            text="IP Configuration Tool",
            style="Title.TLabel"
        ).pack(
            anchor="w"
        )

        ttk.Label(
            self.main,
            text="Manage network configurations quickly and safely.",
            style="Subtitle.TLabel"
        ).pack(
            anchor="w",
            pady=(3, SECTION_GAP)
        )

    # -------------------------
    # Network Section
    # -------------------------

    def build_network_section(self):

        card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=16
        )

        card.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        ttk.Label(
            card,
            text="NETWORK",
            style="Section.TLabel"
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, MEDIUM_GAP)
        )

        ttk.Label(
            card,
            text="Network Type",
            style="Label.TLabel"
        ).grid(
            row=1,
            column=0,
            sticky="w"
        )

        self.app.network = ttk.Combobox(
            card,
            state="readonly",
            values=["Ethernet", "Wi-Fi"],
            width=20
        )

        self.app.network.current(0)

        self.app.network.grid(
            row=2,
            column=0,
            sticky="ew",
            pady=(3, 0)
        )

        self.app.network.bind(
            "<<ComboboxSelected>>",
            lambda event: self.app.refresh()
        )

        info = tk.Frame(
            card,
            bg=WHITE
        )

        info.grid(
            row=1,
            column=1,
            rowspan=2,
            sticky="e",
            padx=(20, 0)
        )

        status_row = tk.Frame(
            info,
            bg=WHITE
        )

        status_row.pack(
            anchor="e"
        )

        self.app.status_dot = tk.Label(
            status_row,
            text="●",
            fg=SUCCESS,
            bg=WHITE,
            font=("Segoe UI", 11, "bold")
        )

        self.app.status_dot.pack(
            side="left",
            padx=(0, 4)
        )

        self.app.status = ttk.Label(
            status_row,
            text="",
            style="Status.TLabel"
        )

        self.app.status.pack(
            side="left"
        )

        self.app.current = ttk.Label(
            info,
            text="",
            style="Value.TLabel"
        )

        self.app.current.pack(
            anchor="e",
            pady=(4, 0)
        )

        card.columnconfigure(
            0,
            weight=1
        )

    # -------------------------
    # Configuration Section
    # -------------------------

    def build_configuration_section(self):

        card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=16
        )

        card.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        ttk.Label(
            card,
            text="STATIC CONFIGURATION",
            style="Section.TLabel"
        ).pack(
            anchor="w",
            pady=(0, MEDIUM_GAP)
        )

        ttk.Label(
            card,
            text="Configuration",
            style="Label.TLabel"
        ).pack(
            anchor="w"
        )

        self.app.config = ttk.Combobox(
            card,
            state="readonly"
        )

        self.app.config.pack(
            fill="x",
            pady=(3, MEDIUM_GAP)
        )

        self.app.config.bind(
            "<<ComboboxSelected>>",
            lambda event: self.app.show_config()
        )

        self.app.details = ttk.Label(
            card,
            text="",
            style="Value.TLabel",
            justify="left"
        )

        self.app.details.pack(
            anchor="w",
            pady=(2, MEDIUM_GAP)
        )

        button_row = ttk.Frame(
            card,
            style="Card.TFrame"
        )

        button_row.pack(
            fill="x",
            pady=(4, 0)
        )

        ttk.Button(
            button_row,
            text="Ping",
            style="Secondary.TButton",
            command=self.app.do_ping
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        tk.Button(
    button_row,
    text="Apply Configuration",
    bg="#040C7A",
    fg="white",
    activebackground="#0401D6",
    activeforeground="white",
    command=self.app.apply
            ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 0)
        )

        button_row.columnconfigure((0, 1), weight=0)

    # -------------------------
    # Actions Section
    # -------------------------

    def build_actions_section(self):

        card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=16
        )

        card.pack(
            fill="x",
            pady=(0, SECTION_GAP)
        )

        ttk.Label(
            card,
            text="NETWORK ACTIONS",
            style="Section.TLabel"
        ).pack(
            anchor="w",
            pady=(0, MEDIUM_GAP)
        )

        button_row = ttk.Frame(
            card,
            style="Card.TFrame",
            padding=(10, 0)
        )

        button_row.pack(
            anchor="w"
        )

        tk.Button(
    button_row,
    text="Set IP to DHCP",
    bg="#188602",
    fg="white",
    activebackground="#39C004",
    activeforeground="white",
    command=self.app.dhcp
).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ttk.Button(
            button_row,
            text="Refresh",
            
            style="Secondary.TButton",
            command=self.app.refresh
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 0)
        )

        tk.Button(
    button_row,
    text="Ping Monitor",
    command=self.app.manage,
    bg="#A8AA21",
    fg="white",
    activebackground="#B5D404",
    activeforeground="white",
    font=("Arial", 10, "bold"),
    relief="raised",
).grid(
    row=0,
    column=2,
    sticky="w",
    padx=(8, 0)
)

        button_row.columnconfigure((0, 1, 2), weight=0)

    # -------------------------
    # Activity / Log
    # -------------------------

    def build_log_section(self):

        card = ttk.Frame(
            self.main,
            style="Card.TFrame",
            padding=16
        )

        card.pack(
            fill="both",
            expand=True
        )

        ttk.Label(
            card,
            text="ACTIVITY",
            style="Section.TLabel"
        ).pack(
            anchor="w",
            pady=(0, MEDIUM_GAP)
        )

        self.app.log = tk.Text(
            card,
            height=6,
            state="disabled",
            bg=LIGHT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="solid",
            borderwidth=1,
            highlightthickness=0,
            font=("Consolas", 9),
            padx=10,
            pady=8
        )

        self.app.log.pack(
            fill="both",
            expand=True
        )

    # -------------------------
    # Footer
    # -------------------------

    def build_footer(self):
        ttk.Label(
            self.main,
            text="サイラム",
            style="Subtitle.TLabel"
        ).pack(
            anchor="center",
            pady=(10, 0)
        )