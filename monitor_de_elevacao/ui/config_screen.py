from .device_config_table import DeviceConfigTable
from .limit_card import LimitCard
from tkinter import filedialog
import customtkinter as ctk
from ..infra import data

class ConfigScreen(ctk.CTkFrame):
    
    def __init__(self, parent: ctk.CTkFrame, controller) -> None:
        
        super().__init__(parent)
        self.controller = controller

        # ---------------------------------------------
        # -- Screen variables
        # ---------------------------------------------

        self.file_path_var = ctk.StringVar(value="")
        self.num_devices_var = ctk.StringVar(value="1")  # Number of circuit brakers
        self.num_poles_var = ctk.StringVar(value="1")  # Number of poles per device
        self.device_tables: list[DeviceConfigTable] = []  # List with the table of each breaker
        self.limit_cards: list[LimitCard] = []  # List with each limit card
        self.max_card_per_row = 6  # Maximum number of limit cards per row

        # ---------------------------------------------
        # -- Grid basic layout
        # ---------------------------------------------
        # Row 0: upper bar (title + template buttons)
        # Row 1: file selection
        # Row 2: devices + poles combo boxes
        # Row 3: dynamic tables
        # Row 4: limit cards
        # Row 5: change screen button

        # Dynamic tables can grow in height but not the limit cards
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------
        # -- 0) Upper bar (title + buttons)
        # ---------------------------------------------

        top_bar = ctk.CTkFrame(self)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_bar.grid_rowconfigure(0, weight=1)
        top_bar.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(top_bar, text="Settings", font=("Arial", 36))
        title.grid(row=0, column=0, sticky="w")

        btn_load_template = ctk.CTkButton(
            top_bar,
            text="Load template",
            command=self.load_template_stub,
            width=120
        )
        btn_load_template.grid(row=0, column=2, padx=5, sticky="e")

        btn_save_template = ctk.CTkButton(
            top_bar,
            text="Save template",
            command=self.save_template_stub,
            width=120
        )
        btn_save_template.grid(row=0, column=3, padx=5, sticky="e")

        # ---------------------------------------------
        # -- Main scrollable frame
        # ---------------------------------------------

        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------
        # -- 1) File selection section
        # ---------------------------------------------

        file_frame = ctk.CTkFrame(main_frame)
        file_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        file_frame.grid_columnconfigure(1, weight=1)

        lbl_file = ctk.CTkLabel(file_frame, text="Original CSV file:")
        lbl_file.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="w")

        entry_file = ctk.CTkEntry(file_frame, textvariable=self.file_path_var)
        entry_file.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="ew")

        btn_browse = ctk.CTkButton(
            file_frame,
            text = "Select file",
            command = self.select_file
        )
        btn_browse.grid(row=0, column=2, padx=(0, 5), pady=5)

        # ---------------------------------------------
        # -- 2) Devices and poles combo boxes
        # ---------------------------------------------

        combo_frame = ctk.CTkFrame(main_frame)
        combo_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        combo_frame.grid_columnconfigure((1, 3, 5, 7), weight=1)

        # Number of circuit breakers
        lbl_devices = ctk.CTkLabel(combo_frame, text="Number of devices:")
        lbl_devices.grid(row=0, column=0, padx=5, pady=0, sticky="w")

        self.combo_devices = ctk.CTkComboBox(
            combo_frame,
            values = [str(i) for i in range(1, data.max_devices+1)],
            variable = self.num_devices_var,
            state = "readonly",
            command = self.on_change_num_devices,
            width = 50
        )
        self.combo_devices.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Number of poles
        lbl_poles = ctk.CTkLabel(combo_frame, text="Number of poles per device:")
        lbl_poles.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.combo_poles = ctk.CTkComboBox(
            combo_frame,
            values = [str(i) for i in range(1, data.max_poles+1)],
            variable = self.num_poles_var,
            state = "readonly",
            command = self.on_change_num_poles,
            width = 50
        )
        self.combo_poles.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Ambient temperature channel
        lbl_ambient_tmp_1 = ctk.CTkLabel(combo_frame, text="Ambient temperature channel 1")
        lbl_ambient_tmp_1.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        self.amb_tmp_1 = ctk.CTkEntry(combo_frame, width=50)
        self.amb_tmp_1.grid(row=0, column=5, padx=5, pady=5, sticky="w")

        lbl_ambient_tmp_2 = ctk.CTkLabel(combo_frame, text="Ambient temperature channel 2")
        lbl_ambient_tmp_2.grid(row=0, column=6, padx=5, pady=5, sticky="w")

        self.amb_tmp_2 = ctk.CTkEntry(combo_frame, width=50)
        self.amb_tmp_2.grid(row=0, column=7, padx=5, pady=5, sticky="w")

        # ---------------------------------------------
        # -- 3) Dynamic tables
        # ---------------------------------------------

        self.tables_area = ctk.CTkFrame(main_frame, border_width=1, corner_radius=8)
        self.tables_area.grid(row=3, column=0, sticky="new", padx=10, pady=5)

        # Internal container only for the tables (avoiding mixing grid/pack)
        self.tables_container = ctk.CTkFrame(self.tables_area)
        self.tables_container.pack(fill="both", expand=True, padx=5, pady=5)

        # ---------------------------------------------
        # -- 4) Limit cards
        # ---------------------------------------------

        self.limits_area = ctk.CTkFrame(main_frame, border_width=1, corner_radius=8)
        self.limits_area.grid(row=4, column=0, sticky="new", padx=10, pady=5)
        self.limits_area.grid_columnconfigure(0, weight=1)

        # Header line: title + "Add limit" button
        limits_header = ctk.CTkFrame(self.limits_area)
        limits_header.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        limits_header.grid_columnconfigure(0, weight=1)

        lbl_limits = ctk.CTkLabel(limits_header, text="Limits configurations")
        lbl_limits.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        btn_add_limit = ctk.CTkButton(
            limits_header,
            text="Add limit",
            command=self.add_limit_card,
            width=100
        )
        btn_add_limit.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Container for the limit cards
        self.limits_container = ctk.CTkFrame(self.limits_area)
        self.limits_container.grid(row=1, column=0, sticky="ew", padx=5, pady=(5, 10))

        # ---------------------------------------------
        # -- 5) Button to start monitoring
        # ---------------------------------------------

        btn_go_monitor = ctk.CTkButton(
            self,
            text="Start monitoring",
            command=lambda: controller.show_frame("MonitorScreen")
        )
        btn_go_monitor.grid(row=5, column=0, pady=10)

        # Create the initial tables
        self.rebuild_device_tables()

        # Create a first limit card by default
        self.add_limit_card()
    
    def load_template_stub(self) -> None:
        print("Load template")
        print(self.get_config_snapshot())

    def save_template_stub(self) -> None:
        print("Save template")
    
    def select_file(self) -> None:
        """
        Use the windows file explorer to find the csv file
        """

        file_path = filedialog.askopenfilename(
            title = "Select the temperature data logger file",
            filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")]
        )

        if file_path:
            self.file_path_var.set(file_path)

    def on_change_num_devices(self, value: str):
        print("Number of devices:", value)
        self.num_devices_var.set(value)
        self.rebuild_device_tables()
    
    def on_change_num_poles(self, value: str):
        print("Number of poles:", value)
        self.num_poles_var.set(value)
        self.rebuild_device_tables()

    def rebuild_device_tables(self) -> None:
        """
        Recreate ALL the device tables based on the number of devices and poles
        """
        
        # 1) Destroy old tables
        for tbl in self.device_tables:
            tbl.destroy()
        self.device_tables.clear()

        # 2) Read the current combo box values
        try:
            num_devices = int(self.num_devices_var.get())
            num_poles = int(self.num_poles_var.get())
        except ValueError:
            return
        
        # 3) Create the new tables
        for i in range(num_devices):
            tbl = DeviceConfigTable(
                parent = self.tables_container,
                device_index = i+1,
                num_poles = num_poles
            )
            tbl.grid(row=i, column=0, sticky="ew", padx=5, pady=5)
            
            self.tables_container.grid_columnconfigure(i, weight=0)
            self.device_tables.append(tbl)

        # Ensure column 0 of the container expands
        self.tables_container.grid_columnconfigure(0, weight=1)
    
    def add_limit_card(self) -> None:
        """
        Create a new limit card and place it in the grid from the left to the right, then breaking into a new row after max_cards_per_row cards.
        """
        card = LimitCard(
            parent=self.limits_container,
            index=len(self.limit_cards)+1,
            on_delete=self.remove_limit_card
        )
        self.limit_cards.append(card)
        self.replace_limit_cards()

    def remove_limit_card(self, card: LimitCard) -> None:
        """
        Remove a limit card from the list
        """

        if card in self.limit_cards:
            self.limit_cards.remove(card)
        
        # Destroy the widget
        card.destroy()

        # Reorganize the grid
        self.replace_limit_cards()

    def replace_limit_cards(self) -> None:

        for i, card in enumerate(self.limit_cards, start=1):
            card.set_index(i)
            row = (i-1) // self.max_card_per_row
            col = (i-1) % self.max_card_per_row
            card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
    
    def get_config_snapshot(self) -> dict:
        """
        Read all GUI fields and return a pure python representation
        of the current configuration.
        """

        # 1) Basic values
        file_path = self.file_path_var.get().strip()
        
        try:
            num_devices = int(self.num_devices_var.get())
        except ValueError:
            num_devices = 0
        
        try:
            num_poles = int(self.num_poles_var.get())
        except ValueError:
            num_poles = 0

        ambient_channels = [
            self.amb_tmp_1.get().strip(),
            self.amb_tmp_2.get().strip()
        ]

        # 2) Devices
        devices: list[dict] = []
        for index, device in enumerate(self.device_tables, start=1):
            channels = device.get_channels()
            devices.append(
                {
                    "index": index,
                    "channels": channels
                }
            )
        
        # 3) Limits
        limits = [card.to_dict() for card in self.limit_cards]

        # 4) Create a full snapshot
        snapshot = {
            "file_path": file_path,
            "ambient":{
                "channels": ambient_channels,
            },
            "num_devices": num_devices,
            "num_poles": num_poles,
            "devices": devices,
            "limits": limits,
        }

        return snapshot