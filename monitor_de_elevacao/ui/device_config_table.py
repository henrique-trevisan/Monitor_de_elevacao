import customtkinter as ctk
from ..infra import data

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
        
    def get_channels(self) -> list[str]:
        """
        Return all the channels configured for this device,
        in the same order they were used to build the table.
        """

        values: list[str] = []
        for entry in self.channel_entries:
            values.append(entry.get().strip())
            
        return values