from tkinter import filedialog, messagebox
import customtkinter as ctk
from ..infra import data
import queue
import time

class App(ctk.CTk):

    def __init__(self) -> None:

        super().__init__()

        # Widow basic settings
        self.title("Circuit breaker monitor")
        self.geometry("1024x768")
        self.minsize(800, 600)

        # Appearance and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Main frame
        self.root = ctk.CTkFrame(self)
        self.root.pack(fill="both", expand=True)

        # Ensure the main frame expand correctly
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Dictionary to store the screens
        self._frames: dict[str, ctk.CTkFrame] = {}
        
        # Attach the close button to the withdrow action
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Create and register the screens
        self._init_frames()

        # Starts at the settings screen
        self.show_frame("ConfigScreen")

        # Starts monitoring the tray queue
        self.after(100, self.pull_tray_queue)

        # Begin the main loop
        self.mainloop()
    
    def _init_frames(self) -> None:
        """
        Create the tables and register in the dictionary
        """
        for FrameClass in (ConfigScreen, MonitorScreen):
            frame = FrameClass(parent=self.root, controller=self)  # Instantiates the screen
            name = FrameClass.__name__  # Get the name for the screen
            self._frames[name] = frame  # Saves in the dictionary
            frame.grid(row=0, column=0, sticky="nsew")  # Exibits in the frame
    
    def show_frame(self, name: str) -> None:
        """
        Bring the desired screen forward and update the monitoring variable
        """
        frame = self._frames.get(name)  # Get the screen instance from the dict
        if frame is None:
            raise ValueError(f"Screen '{name}' is not registered.")

        data.monitoring = True if name == "MonitorScreen" else False

        frame.tkraise()
    
        # Update the picture of the icon and the menu
        data.icon.icon = data.icon_monitoring if data.monitoring else data.icon_awaiting
        data.icon.update_menu()
        
        print(f"Monitorando: {data.monitoring}, tela: {name}")
        
    
    def show_window(self) -> None:
        """
        Show the minimized window back from the system tray
        """
        self.deiconify()
        self.lift()
        self.focus_force()

    def on_window_close(self) -> None:
        """
        When the user press on the X, it minimizes to the tray
        """
        self.withdraw()
    
    def exit_confirm(self, icon) -> None:
        confirmation = messagebox.askyesno(
            "Exit",
            "Are you sure you want to exit the monitor?"
        )

        if confirmation:
            # Ask to the worker thread to stop
            data.worker_stop = True

            # Stop the tray icon
            icon.stop()

            # Destroy the window and finish the main loop
            self.destroy()
    
    def pull_tray_queue(self) -> None:
        """
        Checks periodically for commands from the tray
        """
        
        # Recover an item from the tray
        try:
            command = data.tray_queue.get_nowait()
        except queue.Empty:
            command = None
        
        if command is not None:
            match command[0]:
                case "show_window":
                    self.root.after(0, self.show_window)
                case "toggle_monitoring":
                    self.show_frame("ConfigScreen" if data.monitoring else "MonitorScreen")
                case "exit":
                    self.exit_confirm(command[2])

        # Schedule the next pull
        self.after(100, self.pull_tray_queue)


class DeviceConfigTable(ctk.CTkFrame):
    """
    Represent the setting table of a single device.
    """

    def __init__(self, parent: ctk.CTkFrame, device_index: int, num_poles: int) -> None:
        super().__init__(parent)

        self.device_index = device_index
        self.num_poles = num_poles

        # Basic grid setting: row 0 for title, col >= 1 for poles
        self.grid_columnconfigure(0, weight=0)
        for col in range(1, num_poles*2 + len(data.other_measures_names) + 1):
            self.grid_columnconfigure(col, weight=1)

        # Row 0: Title + headers
        lbl_title = ctk.CTkLabel(self, text=f"Circuit\nbreaker #{device_index}")
        lbl_title.grid(row=0, column=0, padx=5, pady=5)

        for pole in range(1, num_poles+1):
            lbl_up = ctk.CTkLabel(self, text=f"Upper\npole {pole}")
            lbl_up.grid(row=0, column=2*pole-1, padx=5, pady=5, sticky="ew")

            lbl_low = ctk.CTkLabel(self, text=f"Lower\npole {pole}")
            lbl_low.grid(row=0, column=2*pole, padx=5, pady=5, sticky="ew")
        
        for idx, value in enumerate(data.other_measures_names):
            lbl = ctk.CTkLabel(self, text = value)
            lbl.grid(row=0, column=2*num_poles + idx + 1, padx=5, pady=5, sticky="ew")

        # Row 2: Text input for the channel name
        self.channel_entries: list[ctk.CTkEntry] = []

        lbl_channel = ctk.CTkLabel(self, text="Data logger\nchannel:")
        lbl_channel.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        for channel in range(1, num_poles*2 + len(data.other_measures_names) + 1):
            entry = ctk.CTkEntry(self)
            entry.grid(row=1, column=channel, padx=5, pady=5, sticky="ew")
            self.channel_entries.append(entry)

class LimitCard(ctk.CTkFrame):
    """
    Represent a single limit card
    """

    def __init__(self, parent: ctk.CTkFrame, index:int, on_delete) -> None:
        super().__init__(parent)

        self.index = index
        self.on_delete = on_delete

        # Variable to sotore card data
        self.name_var = ctk.StringVar()
        self.value_var = ctk.StringVar()

        # Grid config for the card itself
        self.grid_columnconfigure(0, weight=1)

        # Row 0: Title
        self.lbl_title = ctk.CTkLabel(self, text=f"Limit #{self.index}")
        self.lbl_title.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Row 1: Channel
        lbl_channel = ctk.CTkLabel(self, text=f"Channel or\nchannel's nickname")
        lbl_channel.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        # Row 2: Channel identification
        entry_channel = ctk.CTkEntry(self, textvariable=self.name_var, width=50)
        entry_channel.grid(row=2, column=0, padx=5, pady=(2, 5), sticky="ew")

        # Row 3: Limit
        lbl_limit = ctk.CTkLabel(self, text="Limit [\U00000394°C]")
        lbl_limit.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

        # Row 4: Limit input
        entry_limit = ctk.CTkEntry(self, textvariable=self.value_var, width=50)
        entry_limit.grid(row=4, column=0, padx=5, pady=(2, 5), sticky="ew")

        # Row 5: Delete limit
        btn_delete = ctk.CTkButton(
            self,
            text="Delete\nlimit",
            command=lambda: self.on_delete(self)
        )
        btn_delete.grid(row=5, column=0, padx=5, pady=(10, 5), sticky="ew")

    def set_index(self, new_index: int) -> None:

        self.index = new_index
        self.lbl_title.configure(text=f"Limit #{self.index}")


class ConfigScreen(ctk.CTkFrame):
    
    def __init__(self, parent: ctk.CTkFrame, controller: App) -> None:
        
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
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=0)
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
        # -- 1) File selection section
        # ---------------------------------------------

        file_frame = ctk.CTkFrame(self)
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

        combo_frame = ctk.CTkFrame(self)
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

        self.tables_area = ctk.CTkFrame(self, border_width=1, corner_radius=8)
        self.tables_area.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

        # Internal container only for the tables (avoiding mixing grid/pack)
        self.tables_container = ctk.CTkFrame(self.tables_area)
        self.tables_container.pack(fill="both", expand=True, padx=5, pady=5)

        # ---------------------------------------------
        # -- 4) Limit cards
        # ---------------------------------------------

        self.limits_area = ctk.CTkFrame(self, border_width=1, corner_radius=8)
        self.limits_area.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
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

class MonitorScreen(ctk.CTkFrame):

    def __init__(self, parent: ctk.CTkFrame, controller: App) -> None:

        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Monitor screen", font=("Arial", 24))
        title.pack(pady=20)


        info = ctk.CTkLabel(
            self,
            text=(
                "Aqui depois vão aparecer:\n"
                "- Tabelas espelhando a configuração (quantidade/colunas)\n"
                "- Cards de limites com valor lido\n"
                "- Tudo em modo somente leitura\n"
            ),
            justify="left",
        )
        info.pack(pady=10)

        btn_go_config = ctk.CTkButton(
            self,
            text="Stop monitoring",
            command=lambda: controller.show_frame("ConfigScreen"),
        )
        btn_go_config.pack(pady=20, side="bottom")