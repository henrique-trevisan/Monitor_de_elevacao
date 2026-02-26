from .ambient_tables import AmbientTables, AmbientStatsTable
from .device_monitor_table import DeviceMonitorGroup
from .limit_monitor_card import LimitMonitorCard
from .status_banner import MonitoringStatusBanner
import customtkinter as ctk
from ..infra import data

class MonitorScreen(ctk.CTkFrame):
    """
    Screen to display the test temperatures
    """

    def __init__(self, parent: ctk.CTkFrame, controller) -> None:

        super().__init__(parent)
        self.controller = controller

        # ---------------------------------------------
        # -- Internal states
        # ---------------------------------------------

        self.led_state: bool = False
        self.led_after_id: str | None = None
        self.device_groups: list[DeviceMonitorGroup] = []

        # Build the monitor screen
        self.build_widgets()

    def build_widgets(self):
        """
        General screen layout: grid
        Row 0: Top bar
        Row 1: Scrollable area with table/cards
        Row 3: Button to return to settings
        """

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------
        # -- Row 0) Top bar (title + "LED")
        # ---------------------------------------------

        top_bar = ctk.CTkFrame(self)
        top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        top_bar.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(top_bar, text="Monitoring", font=("Arial", 36))
        title.grid(row=0, column=0, sticky="w")

        # "LED" indicator (● green/grey)
        self.led_label = ctk.CTkLabel(
            top_bar,
            text="●",
            font=("Arial", 36),
            text_color="grey"
        )
        self.led_label.grid(row=0, column=2, sticky="e", padx=10)

        # ---------------------------------------------
        # -- Row 1) Main scrollable frame
        # ---------------------------------------------

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        # -----
        # -- Status banner (row 0 inside scroll)
        # -----

        self.status_banner = MonitoringStatusBanner(
            self.scroll_frame,
            on_force_tracking=self.on_force_tracking,
        )
        self.status_banner.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # -----
        # -- Ambient section
        # -----

        self.ambient_frame = ctk.CTkFrame(self.scroll_frame)
        self.ambient_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.ambient_frame.grid_columnconfigure((0, 1), weight=1)

        # Left: ambient table (channel and mean)
        self.ambient_table = AmbientTables(self.ambient_frame, max_rows=6)
        self.ambient_table.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Right: ambient stats table (max/min/delta)
        self.ambient_stats_table = AmbientStatsTable(self.ambient_frame)
        self.ambient_stats_table.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        # -----
        # -- Devices section (one frame per device)
        # -----

        self.devices_frame = ctk.CTkFrame(self.scroll_frame)
        self.devices_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.devices_frame.grid_columnconfigure(0, weight=1)

        # Devices placeholder
        self.devices_placeholder = ctk.CTkLabel(
            self.devices_frame,
            text=(
                "Here will appear, for each device:\n"
                "\t- Table with readings (every x min)\n"
                "\t- Table with deltas vs ambient mean\n"
                "\t- Table with Max / Min / Estab per column"
            ),
            justify="left"
        )
        self.devices_placeholder.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # -----
        # -- Limits section (inside the scroll frame)
        # -----

        self.limits_frame = ctk.CTkFrame(self.scroll_frame)
        self.limits_frame.grid(
            row=3, column=0, sticky="ew", padx=5, pady=5
        )
        self.limits_frame.grid_columnconfigure(0, weight=1)

        lbl_limits_title = ctk.CTkLabel(
            self.limits_frame,
            text="Limits monitoring (ΔT)",
            font=("Arial", 16, "bold"),
        )
        lbl_limits_title.grid(
            row=0, column=0, sticky="w", padx=5, pady=(5, 2)
        )

        # Container that holds the cards (grid)
        self.limits_container = ctk.CTkFrame(self.limits_frame)
        self.limits_container.grid(
            row=1, column=0, sticky="ew", padx=5, pady=(2, 10)
        )
        self.limits_container.grid_columnconfigure(0, weight=1)

        # Placeholder for when there is no data yet
        self.limits_placeholder = ctk.CTkLabel(
            self.limits_container,
            text="No limits data yet.",
            justify="left",
        )
        self.limits_placeholder.grid(
            row=0, column=0, sticky="w", padx=5, pady=5
        )

        # Internal state for limit cards
        self.limit_cards: list[LimitMonitorCard] = []
        self.max_limit_cards_per_row = 4


        # -----
        # -- Label summary (helps for development)
        # -----

        self.summary_label = ctk.CTkLabel(
            self.scroll_frame,
            text="No monitoring data yet.",
            justify="left"
        )
        self.summary_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)

        # ---------------------------------------------
        # -- Row 2) Button to stop monitoring
        # ---------------------------------------------

        # Button to return to settings
        btn_go_config = ctk.CTkButton(
            self,
            text="Stop monitoring",
            command=lambda: self.controller.show_frame("ConfigScreen")
        )
        btn_go_config.grid(row=2, column=0, pady=5)

    # ---------------------------------------------
    # -- Lifecyle hooks
    # ---------------------------------------------

    def on_show(self):
        """
        Called every time the screen is shown.
        Reads data.last_config_snapshot and updates the summary label.
        Starts the LED blinking if monitoring is active.
        """

        # Start/continue LED blinking if it is in monitor mode
        if data.monitoring:
            self.start_led_blink()

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
    
    def start_led_blink(self) -> None:
        """
        Start the led loop if not already started
        """

        if self.led_after_id is None:
            self.toggle_led()
    
    def stop_led_blink(self) -> None:
        """
        Stops the LED blinking loop and sets it to gray
        """

        # Cancel the rescheaduling of the toggle led
        if self.led_after_id is not None:
            self.after_cancel(self.led_after_id)
            # Removes the ID
            self.led_after_id = None

        # Set the state to "off" and change the color back to gray
        self.led_state = False
        self.led_label.configure(text_color="grey")

    def toggle_led(self) -> None:
        """
        Toggle LED color between grey and green while data.monitoring is True
        """

        # If it is not monitoring anymore, stops the loop
        if not data.monitoring:
            self.stop_led_blink()
            return
        
        self.led_state = not self.led_state
        color = "green" if self.led_state else "grey"
        self.led_label.configure(text_color=color)

        # Scheadule the nexte shift and update the ID (for disableing later)
        self.led_after_id = self.after(2000, self.toggle_led)

    def update_from_payload(self, payload: dict) -> None:
        """
        This method will be called by the worker thread via queue
        with a monitoring payload that already contains:
            - status (waiting/monitoring/alert, times)
            - ambient data (6 rows, stats)
            - per-device readings/deltas/results
            - limits status (max deltas)
        """
        count = payload.get("update_index", "?")

        # --- NEW: status banner ---
        status_payload = payload.get("status")
        self.status_banner.update_from_status(status_payload)

        # Ambient
        ambient = payload.get("ambient", {})
        rows = ambient.get("rows", [])
        stats = ambient.get("stats", {})
        self.ambient_table.update_from_rows(rows)
        self.ambient_stats_table.update_from_stats(stats)

        # Devices
        devices_payload = payload.get("devices", [])
        self.rebuild_device_groups(devices_payload)

        # Limits
        limits_payload = payload.get("limits", [])
        self.rebuild_limit_cards(limits_payload)

        # Summary text
        self.summary_label.configure(
            text=(
                f"Monitoring data received (update {count}).\n"
                f"Ambient rows: {len(rows)}\n"
                f"Devices: {len(devices_payload)}\n"
                f"Limits: {len(limits_payload)}"
            )
        )

    def rebuild_device_groups(self, devices_payload: list[dict]) -> None:
        """
        Reconstrói todas as tabelas de dispositivos a partir do payload.
        Substitui o placeholder por uma tabela real quando existir dado.
        """

        # Remove todos os grupos antigos
        for group in getattr(self, "device_groups", []):
            group.destroy()
        self.device_groups = []

        if not devices_payload:
            # Se não tem dispositivo no payload, mostra o placeholder
            self.devices_placeholder.grid(row=0, column=0, sticky="w", padx=5, pady=5)
            return

        # Esconde o placeholder (sem destruir)
        self.devices_placeholder.grid_forget()

        # Para cada dispositivo recebido, cria um bloco
        for row_idx, device_data in enumerate(devices_payload):
            column_labels = device_data.get("column_labels", [])
            device_index = device_data.get("device_index", row_idx + 1)

            group = DeviceMonitorGroup(
                parent=self.devices_frame,
                device_index=device_index,
                column_labels=column_labels,
                max_rows=6,
            )
            group.grid(row=row_idx, column=0, sticky="ew", padx=5, pady=5)

            # Preenche com dados desse dispositivo
            group.update_from_payload(device_data)

            self.device_groups.append(group)
            

    def rebuild_limit_cards(self, limits_payload: list[dict]) -> None:
        """
        Rebuild all limit monitor cards from the given payload.

        Parameters
        ----------
        limits_payload : list[dict]
            List of limit payload dictionaries, as produced by the worker.
        """
        # Destroy old cards
        for card in self.limit_cards:
            card.destroy()
        self.limit_cards.clear()

        # No limits data: show placeholder and return
        if not limits_payload:
            self.limits_placeholder.configure(text="No limits data.")
            self.limits_placeholder.grid(
                row=0, column=0, sticky="w", padx=5, pady=5
            )
            return

        # Hide placeholder
        self.limits_placeholder.grid_forget()

        # Create cards and place them in a grid (row by row)
        for idx, limit_data in enumerate(limits_payload, start=1):
            card = LimitMonitorCard(self.limits_container, index=idx)
            card.update_from_payload(limit_data)

            row = (idx - 1) // self.max_limit_cards_per_row
            col = (idx - 1) % self.max_limit_cards_per_row

            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.limits_container.grid_columnconfigure(col, weight=1)

            self.limit_cards.append(card)
    
    def on_force_tracking(self) -> None:
        """
        Called when the user clicks the 'Track data anyway' button
        in the status banner.

        For now this simply sets a flag in the global data module.
        The worker can read this flag to start monitoring even if
        the elapsed time is smaller than the required minimum.
        """
        # Create or update a simple flag in the shared data module
        setattr(data, "force_track_anyway", True)

        # Optional: update summary label just to help debugging
        current_text = self.summary_label.cget("text")
        extra = "\nUser requested: track data anyway."
        self.summary_label.configure(text=current_text + extra)
