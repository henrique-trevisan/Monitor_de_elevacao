# monitor_de_elevacao/ui/limit_monitor_card.py

from typing import Any, Dict
import customtkinter as ctk


class LimitMonitorCard(ctk.CTkFrame):
    """
    Read-only card used in the monitoring screen to show:
    - limit name
    - configured limit (ΔT)
    - max delta found
    - status (OK / EXCEEDED)
    """

    def __init__(self, parent: ctk.CTkFrame, index: int) -> None:
        """
        Initialize the limit monitor card.

        Parameters
        ----------
        parent : ctk.CTkFrame
            Parent frame that will contain this card.
        index : int
            Card index (1-based) to show in the title.
        """
        super().__init__(parent)
        self.index = index
        self.build_widgets()

    def build_widgets(self) -> None:
        """
        Create and place all internal widgets of the card.
        """
        self.grid_columnconfigure(1, weight=1)

        # Row 0: title (index + name)
        self.lbl_title = ctk.CTkLabel(self, text=f"Limit #{self.index}")
        self.lbl_title.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=5,
            pady=(5, 2),
            sticky="w",
        )

        # Row 1: name
        lbl_name = ctk.CTkLabel(self, text="Name:")
        lbl_name.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.lbl_name_value = ctk.CTkLabel(self, text="-")
        self.lbl_name_value.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Row 2: scope (optional info)
        lbl_scope = ctk.CTkLabel(self, text="Scope:")
        lbl_scope.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.lbl_scope_value = ctk.CTkLabel(self, text="-")
        self.lbl_scope_value.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Row 3: limit value
        lbl_limit = ctk.CTkLabel(self, text="Limit [Δ°C]:")
        lbl_limit.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.lbl_limit_value = ctk.CTkLabel(self, text="-")
        self.lbl_limit_value.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # Row 4: max delta
        lbl_max_delta = ctk.CTkLabel(self, text="Max Δ found [Δ°C]:")
        lbl_max_delta.grid(row=4, column=0, padx=5, pady=2, sticky="w")

        self.lbl_max_delta_value = ctk.CTkLabel(self, text="-")
        self.lbl_max_delta_value.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        # Row 5: status
        lbl_status = ctk.CTkLabel(self, text="Status:")
        lbl_status.grid(row=5, column=0, padx=5, pady=(2, 5), sticky="w")

        self.lbl_status_value = ctk.CTkLabel(self, text="-")
        self.lbl_status_value.grid(row=5, column=1, padx=5, pady=(2, 5), sticky="w")

    # -------------- helpers --------------

    @staticmethod
    def _format_float(value: Any) -> str:
        """
        Convert a numeric value to a string with 1 decimal place.
        """
        if value is None:
            return "-"
        try:
            return f"{float(value):.1f}"
        except (TypeError, ValueError):
            return str(value)

    def update_from_payload(self, data: Dict[str, Any]) -> None:
        """
        Update this card using a limit payload dict.

        Expected keys
        -------------
        name : str
            Name of what is being monitored.
        limit_value : float
            Configured allowed ΔT.
        max_delta : float
            Highest ΔT found according to worker processing.
        status : str
            "ok" or "exceeded".
        scope : str, optional
            A free text describing if it is "device", "all_devices", etc.
        device_index : int, optional
            Device index for single-device limits.
        column_label : str, optional
            Column label of the monitored channel/group.
        """
        name = (data.get("name") or "").strip()
        limit_value = data.get("limit_value", None)
        max_delta = data.get("max_delta", None)
        status = (data.get("status") or "").lower()

        scope = data.get("scope", "")
        device_index = data.get("device_index", None)
        column_label = data.get("column_label", "")

        # Title + name
        self.lbl_title.configure(
            text=f"Limit #{self.index} – {name or '-'}"
        )
        self.lbl_name_value.configure(text=name or "-")

        # Build scope description
        scope_parts: list[str] = []
        if scope:
            scope_parts.append(scope)
        if isinstance(device_index, int):
            scope_parts.append(f"device {device_index}")
        if column_label:
            scope_parts.append(column_label)

        scope_text = ", ".join(scope_parts) if scope_parts else "-"
        self.lbl_scope_value.configure(text=scope_text)

        # Numeric fields
        self.lbl_limit_value.configure(text=self._format_float(limit_value))
        self.lbl_max_delta_value.configure(text=self._format_float(max_delta))

        # Status and color
        if status == "ok":
            status_text = "OK"
            color = "green"
        elif status == "exceeded":
            status_text = "EXCEEDED"
            color = "red"
        else:
            status_text = status.upper() if status else "UNKNOWN"
            color = "grey"

        self.lbl_status_value.configure(text=status_text, text_color=color)
