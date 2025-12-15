from typing import List, Dict, Any
import customtkinter as ctk

class AmbientTables(ctk.CTkFrame):
    """
    Read-only table for ambient channels:
    Row 0: header
    Row 1: channel
    Rows 2..N: samples (t1, t2, mean)
    """

    def __init__(self, parent: ctk.CTkFrame, max_rows: int = 6) -> None:
        
        
        super().__init__(parent)
        self.parent = parent
        self.max_rows = max_rows

        # Matrix to store the labels
        self.cells: List[List[ctk.CTkLabel]] = []

        self.build_widgets()
    
    def build_widgets(self) -> None:
        """
        .
        """

        # Columns settings: 0 = index, 1 = T1, 2 = T2, 3 = Mean
        for column in range(4):
            self.grid_columnconfigure(column, weight=1)
        
        # Header
        headers = ["Sample", "Ambient 1", "Ambient 2", "Mean"]
        for column, text in enumerate(headers):
            lbl = ctk.CTkLabel(self, text=text, font=("Arial", 14, "bold"))
            lbl.grid(row=0, column=column, padx=4, pady=4, sticky="nsew")

        # Construct the matrix one row at a time
        for row in range(1, self.max_rows+1):

            # List to store each column for that row
            row_cells: List[ctk.CTkLabel] = []

            # Index column
            lbl_index = ctk.CTkLabel(self, text=str(row))
            lbl_index.grid(row=row, column=0, padx=4, pady=2, sticky="nsew")
            row_cells.append(lbl_index)

            # Measures and mean columns
            for column in range(1, 4):
                lbl_temp = ctk.CTkLabel(self, text="-")
                lbl_temp.grid(row=row, column=column, padx=4, pady=2, sticky="nsew")
                row_cells.append(lbl_temp)

            # Append the contructed row to the matrix
            self.cells.append(row_cells)
    
    def update_from_rows(self, rows: List[Dict[str, Any]]) -> None:
        """
        Fill the table with up to max_rows entries.
        Each row dict should have keys: "t1", "t2", "mean".
        Extra
        """

        # Update each row
        for i in range(self.max_rows):
            # Check in case the payload have less rows than the table preset
            if i < len(rows):
                # Read the payload
                row_data = rows[i]
                t1 = row_data.get("t1", None)
                t2 = row_data.get("t2", None)
                mean = row_data.get("mean", None)

                # Update the labels
                # cells[i][0] is the index, but it is fixed. No need to update.
                self.cells[i][1].configure(text=self.format_value(t1))
                self.cells[i][2].configure(text=self.format_value(t2))
                self.cells[i][3].configure(text=self.format_value(mean))
            
            # If there are less rows in the payload than in the preset
            else:
                # Clear the labels
                self.cells[i][1].configure(text="-")
                self.cells[i][2].configure(text="-")
                self.cells[i][3].configure(text="-")

    # Static method allow the use of a function outside a instance (without the self and access to any variable from the class)
    @staticmethod
    def format_value(value) -> str:
        """
        Limit the number of decimal plates
        """

        if value is None:
            return "-"
        
        # Try to convert to float and limit to 1 decimal plate
        try:
            return f"{float(value):.1f}"
        # If it fails, return the value as a string
        except (TypeError, ValueError):
            return str(value)

class AmbientStatsTable(ctk.CTkFrame):
    """
    Small table for ambient stats:
        - Mean max
        - Mean min
        - Mean max-min
    """

    def __init__(self, parent: ctk.CTkLabel) -> None:
        super().__init__(parent)

        # Two columns: label and value
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        labels = ["Mean max", "Mean min", "Mean max-min"]
        self.value_labels: list[ctk.CTkLabel] = []

        for row, text in enumerate(labels):
            lbl_name = ctk.CTkLabel(self, text=text)
            lbl_name.grid(row=row, column=0, padx=4, pady=2, sticky="w")

            lbl_value = ctk.CTkLabel(self, text="-")
            lbl_value.grid(row=row, column=1, padx=4, pady=2, sticky="e")
            self.value_labels.append(lbl_value)

    def update_from_stats(self, stats: Dict[str, Any]) -> None:
        """
        Fill the status table from a stats dict with keys:
            "mean_max", "mean_min", "mean_delta".
        """
        
        # Extract the data from the payload
        mean_max = stats.get("mean_max", None)
        mean_min = stats.get("mean_min", None)
        mean_delta = stats.get("mean_delta", None)
        values = [mean_max, mean_min, mean_delta]

        # Update the labels
        for label, value in zip(self.value_labels, values):
            label.configure(text=self.format_value(value))

    # Static method allow the use of a function outside a instance (without the self and access to any variable from the class)
    @staticmethod
    def format_value(value) -> str:
        """
        Limit the number of decimal plates
        """

        if value is None:
            return "-"
        
        # Try to convert to float and limit to 1 decimal plate
        try:
            return f"{float(value):.1f}"
        # If it fails, return the value as a string
        except (TypeError, ValueError):
            return str(value)