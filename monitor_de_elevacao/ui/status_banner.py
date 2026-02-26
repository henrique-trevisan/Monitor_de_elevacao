import customtkinter as ctk
from typing import Any, Callable, Optional, Dict


class MonitoringStatusBanner(ctk.CTkFrame):
    """
    Small status banner shown at the top of the monitoring screen.

    It displays:
    - current status (waiting, monitoring, alert, etc.)
    - elapsed time
    - remaining time until automatic tracking starts
    - a 'Track data anyway' button when in 'waiting' mode.
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        on_force_tracking: Optional[Callable[[], None]] = None,
    ) -> None:
        """
        Initialize the status banner.

        Parameters
        ----------
        parent : ctk.CTkFrame
            Parent frame that will contain this banner.
        on_force_tracking : Callable[[], None], optional
            Callback called when the user clicks the
            'Track data anyway' button.
        """
        super().__init__(parent)
        self.on_force_tracking = on_force_tracking
        self._build_widgets()

    def _build_widgets(self) -> None:
        """
        Create and place all internal widgets of the banner.
        """
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Main status line
        self.label_title = ctk.CTkLabel(
            self,
            text="Status: waiting for worker data",
            font=("Arial", 14, "bold"),
        )
        self.label_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=5,
            pady=(5, 0),
        )

        # Details: elapsed / remaining
        self.label_details = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12),
            justify="left",
        )
        self.label_details.grid(
            row=1,
            column=0,
            sticky="w",
            padx=5,
            pady=(0, 5),
        )

        # Button: Track data anyway (hidden by default)
        self.btn_force = ctk.CTkButton(
            self,
            text="Track data anyway",
            command=self._handle_force_tracking,
            width=140,
        )
        # We initially hide it; will be shown only in 'waiting' mode.
        self.btn_force.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=5,
            pady=5,
            sticky="e",
        )
        self.btn_force.grid_remove()

    def _handle_force_tracking(self) -> None:
        """
        Internal handler for the 'Track data anyway' button.
        Calls the external callback if provided.
        """
        if self.on_force_tracking is not None:
            self.on_force_tracking()

    @staticmethod
    def _format_minutes(value: Any) -> str:
        """
        Format a numeric number of minutes for display.
        """
        if value is None:
            return "-"
        try:
            return f"{float(value):.1f} min"
        except (TypeError, ValueError):
            return str(value)

    def update_from_status(self, status: Optional[Dict[str, Any]]) -> None:
        """
        Update banner text and button visibility according to
        the monitoring status payload.

        Expected keys (all optional)
        ----------------------------
        mode : str
            "waiting", "monitoring", "alert_limit", "alert_stable", etc.
        elapsed_minutes : float
            Elapsed time in minutes.
        required_minutes : float
            Required time in minutes for automatic tracking.
        """
        if not status:
            # No status yet: generic message
            self.label_title.configure(text="Status: waiting for worker data")
            self.label_details.configure(text="")
            self.btn_force.grid_remove()
            return

        mode = (status.get("mode") or "monitoring").lower()
        elapsed = status.get("elapsed_minutes", None)
        required = status.get("required_minutes", None)

        # Compute remaining time, if possible
        if elapsed is not None and required is not None:
            try:
                remaining = max(float(required) - float(elapsed), 0.0)
            except (TypeError, ValueError):
                remaining = None
        else:
            remaining = None

        # Build details text
        parts: list[str] = []
        if elapsed is not None:
            parts.append(f"Elapsed: {self._format_minutes(elapsed)}")
        if remaining is not None:
            parts.append(
                f"Auto tracking in: {self._format_minutes(remaining)}"
            )
        details_text = " | ".join(parts)

        # Choose title text and button visibility based on mode
        if mode == "waiting":
            title_text = "Status: waiting for enough data"
            # Show the 'Track data anyway' button
            self.btn_force.grid()
        elif mode == "monitoring":
            title_text = "Status: monitoring active"
            self.btn_force.grid_remove()
        elif mode == "alert_limit":
            title_text = "Status: limit exceeded (monitoring stopped)"
            self.btn_force.grid_remove()
        elif mode == "alert_stable":
            title_text = "Status: stability reached (monitoring stopped)"
            self.btn_force.grid_remove()
        else:
            title_text = f"Status: {mode}"
            self.btn_force.grid_remove()

        self.label_title.configure(text=title_text)
        self.label_details.configure(text=details_text)