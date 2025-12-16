# tests/test_limit_monitor_card_manual.py

import sys
from pathlib import Path
import customtkinter as ctk  # type: ignore

# Adjust sys.path to import the project package
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from monitor_de_elevacao.ui.limit_monitor_card import LimitMonitorCard


def build_fake_limits_payload() -> list[dict]:
    """
    Build a small list of fake limits payloads to visually test the cards.
    """
    return [
        {
            "name": "Front (device 1)",
            "limit_value": 50.0,
            "max_delta": 47.3,
            "status": "ok",
            "scope": "device",
            "device_index": 1,
            "column_label": "Front",
        },
        {
            "name": "Handle (all devices)",
            "limit_value": 60.0,
            "max_delta": 62.1,
            "status": "exceeded",
            "scope": "all_devices",
            "column_label": "Handle",
        },
        {
            "name": "Left side (device 2)",
            "limit_value": 45.0,
            "max_delta": 30.0,
            "status": "ok",
            "scope": "device",
            "device_index": 2,
            "column_label": "Left side",
        },
    ]


def main() -> None:
    """
    Run a simple manual GUI test for LimitMonitorCard.
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("LimitMonitorCard manual test")
    root.geometry("900x400")

    container = ctk.CTkFrame(root)
    container.pack(fill="both", expand=True, padx=10, pady=10)
    container.grid_columnconfigure((0, 1, 2), weight=1)

    limits_payload = build_fake_limits_payload()

    cards: list[LimitMonitorCard] = []
    for idx, limit_data in enumerate(limits_payload, start=1):
        card = LimitMonitorCard(container, index=idx)
        card.update_from_payload(limit_data)

        col = idx - 1  # single row, multiple columns
        card.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        cards.append(card)

    root.mainloop()


if __name__ == "__main__":
    main()
