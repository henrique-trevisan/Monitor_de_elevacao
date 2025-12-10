import customtkinter as ctk
from ..infra import data

class MonitorScreen(ctk.CTkFrame):

    def __init__(self, parent: ctk.CTkFrame, controller) -> None:

        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Monitor screen", font=("Arial", 24))
        title.pack(pady=20)

        # Label to be used during test when the screen shows
        self.summary_label = ctk.CTkLabel(
            self,
            text="No configuration loaded yet",
            justify="left",
        )
        self.summary_label.pack(pady=10)

        btn_go_config = ctk.CTkButton(
            self,
            text="Stop monitoring",
            command=lambda: controller.show_frame("ConfigScreen"),
        )
        btn_go_config.pack(pady=20, side="bottom")

    def on_show(self):
        """
        Called every time the screen is shown.
        Reads data.last_config_snapshot and updates the summary label.
        """

        # 1) Reads the snapshot from the user input
        snapshot = getattr(data, "last_config_snapshot", None)

        if not snapshot:
            self.summary_label.configure(text="No configuration loaded yet.")
            return
        
        num_devices = snapshot.get("num_devices", 0)
        num_poles = snapshot.get("num_poles", 0)
        limits = snapshot.get("limits", [])
        num_limits = len(limits)
        file_path = snapshot.get("file_path", "")

        text = (
            "Current configuration:\n"
            f"\t- File: {file_path or '(not set)'}\n"
            f"\t- Devices: {num_devices}\n"
            f"\t- Poles per device: {num_poles}\n"
            f"\t- Limits: {num_limits}"
        )

        self.summary_label.configure(text=text)
