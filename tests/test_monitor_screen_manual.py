# tests/test_monitor_screen_manual.py

import sys
from pathlib import Path

# -------------------------------------------------------------------
# Adjust sys.path so we can import the project package
# -------------------------------------------------------------------
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import customtkinter as ctk  # type: ignore

from monitor_de_elevacao.ui.monitor_screen import MonitorScreen
from monitor_de_elevacao.infra import data


# -------------------------------------------------------------------
# Helpers to build fake payloads for manual GUI testing
# -------------------------------------------------------------------


def build_fake_snapshot() -> dict:
    """
    Build a minimal configuration snapshot so that
    MonitorScreen.on_show() can display a summary text.
    """
    return {
        "file_path": r"C:\fake\example.csv",
        "ambient": {
            "channels": ["ch01", "ch02"],
        },
        "num_devices": 2,
        "num_poles": 2,
        "devices": [],
        # Snapshot limits in the same style as ConfigScreen persistence
        "limits": [
            {"name": "Handle (device #1)", "value": 60.0},
            {"name": "Left side (device #2)", "value": 50.0},
        ],
    }


def build_fake_limits_payload(devices_payload: list[dict]) -> list[dict]:
    """
    Build example limits payload based on the devices payload.

    The idea is:
    - create one 'ok' limit for Handle (device #1)
    - create one 'exceeded' limit for Left side (device #2)
    """
    if not devices_payload:
        return []

    # We assume all devices share the same column_labels
    base_labels = devices_payload[0].get("column_labels", [])
    try:
        handle_idx = base_labels.index("Handle")
        left_idx = base_labels.index("Left side")
    except ValueError:
        # If labels are different for some reason, just skip limits
        return []

    def find_device(device_index: int) -> dict:
        for dev in devices_payload:
            if dev.get("device_index") == device_index:
                return dev
        raise ValueError(f"Device {device_index} not found in devices_payload")

    dev1 = find_device(1)
    dev2 = find_device(2)

    # These are the maximum deltas already computed by the fake device payload
    dev1_max_handle = dev1["result"]["max"][handle_idx]
    dev2_max_left = dev2["result"]["max"][left_idx]

    limits: list[dict] = []

    # Limit that is NOT exceeded (status = ok)
    limits.append(
        {
            "name": "Handle (device #1)",
            "limit_value": dev1_max_handle + 5.0,  # above actual max
            "max_delta": dev1_max_handle,
            "status": "ok",
            "scope": "device",
            "device_index": 1,
            "column_label": "Handle",
        }
    )

    # Limit that IS exceeded (status = exceeded)
    limits.append(
        {
            "name": "Left side (device #2)",
            "limit_value": dev2_max_left - 0.5,  # below actual max
            "max_delta": dev2_max_left,
            "status": "exceeded",
            "scope": "device",
            "device_index": 2,
            "column_label": "Left side",
        }
    )

    return limits


def build_fake_monitor_payload() -> dict:
    """
    Build a monitoring payload with:
      - 6 ambient rows (t1, t2, mean)
      - 2 devices, 4 columns each (readings/deltas/results)
      - a list of limits, compatible with MonitorScreen.update_from_payload().
    """

    # 1) Ambient: 6 samples
    ambient_rows = []
    base_mean = 25.0

    for i in range(6):
        t1 = base_mean + 0.1 * i
        t2 = base_mean + 0.2 + 0.1 * i
        mean = (t1 + t2) / 2.0
        ambient_rows.append({"t1": t1, "t2": t2, "mean": mean})

    mean_values = [row["mean"] for row in ambient_rows]
    mean_max = max(mean_values)
    mean_min = min(mean_values)
    mean_delta = mean_max - mean_min

    ambient_stats = {
        "mean_max": mean_max,
        "mean_min": mean_min,
        "mean_delta": mean_delta,
    }

    # 2) Devices: same number of columns for readings / deltas / result
    column_labels = ["Upper pole 1", "Lower pole 1", "Left side", "Handle"]
    n_cols = len(column_labels)

    def make_device(device_index: int, offset: float) -> dict:
        """
        Build a fake device block based on ambient mean.
        offset is used so that devices #1 and #2 differ slightly.
        """
        readings: list[list[float]] = []
        deltas: list[list[float]] = []

        # Use ambient mean only to generate coherent numbers
        for i, row in enumerate(ambient_rows):
            mean = row["mean"]

            r_row: list[float] = []
            d_row: list[float] = []
            for j in range(n_cols):
                temp = mean + 10.0 + offset + j + 0.1 * i
                r_row.append(temp)
                d_row.append(temp - mean)
            readings.append(r_row)
            deltas.append(d_row)

        # Compute max / min / estab per column from deltas
        max_vals: list[float] = []
        min_vals: list[float] = []
        estab_vals: list[float] = []

        for col in range(n_cols):
            col_values = [row[col] for row in deltas]
            c_max = max(col_values)
            c_min = min(col_values)
            c_estab = c_max - c_min
            max_vals.append(c_max)
            min_vals.append(c_min)
            estab_vals.append(c_estab)

        return {
            "device_index": device_index,
            "column_labels": column_labels,
            "readings": readings,
            "deltas": deltas,
            "result": {
                "max": max_vals,
                "min": min_vals,
                "estab": estab_vals,
            },
        }

    devices_payload = [
        make_device(device_index=1, offset=0.0),
        make_device(device_index=2, offset=1.0),
    ]

    # 3) Limits, built using the device result data
    limits_payload = build_fake_limits_payload(devices_payload)

    monitor_payload = {
        "update_index": 1,
        "status": {
            "mode": "waiting",
            "elapsed_minutes": 120.0,
            "required_minutes": 240.0,
        },
        "ambient": {
            "rows": ambient_rows,
            "stats": ambient_stats,
        },
        "devices": devices_payload,
        "limits": limits_payload,
    }

    return monitor_payload


# -------------------------------------------------------------------
# Manual test entry point
# -------------------------------------------------------------------


def main() -> None:
    """
    Run a manual GUI test for MonitorScreen:
    - creates a fake configuration snapshot
    - sends a single fake monitoring payload after 500 ms
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("MonitorScreen manual test")
    root.geometry("1200x800")

    # Minimal controller implementation (MonitorScreen expects a controller)
    class DummyController:
        def show_frame(self, name: str) -> None:
            print(f"DummyController.show_frame({name}) called")

    controller = DummyController()

    # Create the monitoring screen
    screen = MonitorScreen(parent=root, controller=controller)
    screen.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Leave the system in monitoring mode so the LED will blink
    data.monitoring = True

    # Minimal snapshot so on_show() can build the summary text
    data.last_config_snapshot = build_fake_snapshot()

    # Call on_show hook
    screen.on_show()

    # Schedule a monitoring payload after a short delay (simulate worker queue)
    fake_payload = build_fake_monitor_payload()
    root.after(500, lambda: screen.update_from_payload(fake_payload))

    root.mainloop()


if __name__ == "__main__":
    main()