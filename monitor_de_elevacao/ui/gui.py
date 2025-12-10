from ..infra.persistence_file import PersistenceFile
from .monitor_screen import MonitorScreen
from .config_screen import ConfigScreen
from tkinter import messagebox
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

        # Instantiate the persistence directory and file
        self.persistence = PersistenceFile()

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
        
        # After the frames are created, try to load the persisted config
        snapshot = self.persistence.load_snapshot()
        if snapshot is None:
            print("No persistence file found.")
            return

        data.last_config_snapshot = snapshot
        config_frame = self._frames.get("ConfigScreen")
        if config_frame is not None:
            config_frame.apply_snapshot(snapshot)
    
    def show_frame(self, name: str) -> None:
        """
        Bring the desired screen forward and update the monitoring variable
        """
        frame = self._frames.get(name)  # Get the screen instance from the dict
        if frame is None:
            raise ValueError(f"Screen '{name}' is not registered.")

        data.monitoring = True if name == "MonitorScreen" else False

        frame.tkraise()

        # If the frame has the attribute 'on_show', execute it
        if hasattr(frame, 'on_show'):
            frame.on_show()
    
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