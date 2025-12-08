import customtkinter as ctk

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