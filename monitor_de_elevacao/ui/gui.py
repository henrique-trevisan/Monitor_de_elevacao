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
        # -- Upper bar
        # ---------------------------------------------

        top_bar = ctk.CTkFrame(self)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_bar.grid_rowconfigure(0, weight=1)

        title = ctk.CTkLabel(top_bar, text="Settings", font=("Arial", 36))
        title.grid(row=0, column=0, sticky="w")

        btn_load_template = ctk.CTkButton(
            top_bar,
            text="Load template",
            command=self.load_template_stub,
            width=120
        )
        btn_load_template.grid(row=0, column=1, padx=5, sticky="e")

        btn_save_template = ctk.CTkButton(
            top_bar,
            text="Save template",
            command=self.save_template_stub,
            width=120
        )
        btn_save_template.grid(row=0, column=2, padx=5, sticky="e")

        info = ctk.CTkLabel(
            self,
            text=(
                "Aqui depois vão entrar:\n"
                "- Seleção de arquivo\n"
                "- Combobox de número de disjuntores\n"
                "- Combobox de número de polos\n"
                "- Tabelas dinâmicas\n"
                "- Cards de limites\n"
                "- Botões de carregar/salvar template"
            ),
            justify="left",
        )
        info.grid(row=1, column=0, pady=10)

        # Button to start monitoring
        btn_go_monitor = ctk.CTkButton(
            self,
            text="Start monitoring",
            command=lambda: controller.show_frame("MonitorScreen")
        )
        btn_go_monitor.grid(row=3, column=0, pady=20, sticky="s")
    
    def load_template_stub(self) -> None:
        ...

    def save_template_stub(self) -> None:
        ...

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