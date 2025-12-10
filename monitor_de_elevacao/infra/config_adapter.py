# monitor_de_elevacao/infra/config_adapter.py

from __future__ import annotations

from typing import Any, Dict, List
from . import data

class ConfigAdapter:
    """
    Responsible for:
        - Convert the GUI snapshot for the payload format expected by the worker.
        - Pushes tasks to the data queue
    """

    def snapshot_to_worker_payload(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts the snapshot from the GUI to the payload format
        expected by the worker (data.user_input_variables["payload"]).

        No side effects; Only transforms data.
        """

        # 1) File
        file_directory = snapshot.get("file_path", "").strip()

        # 2) Ambient temperature
        ambient_channels: List[str] = snapshot.get("ambient", {}).get("channels", [])
        ambient_channels = [channel.strip() for channel in ambient_channels]
        # ambient_number = sum(1 for ch in ambient_channels if ch)
        ambient_number = len(ambient_channels)

        ambient = {
            "ambient_number": ambient_number,
            "ambient_channels": ambient_channels,
        }

        # 3) Circuit breakers
        num_devices = int(snapshot.get("num_devices", 0) or 0)
        num_poles = int(snapshot.get("num_poles", 0) or 0)

        devices_snapshot: List[Dict[str, Any]] = snapshot.get("devices", [])

        connected_channels: List[Dict[str, Any]] = []

        for device in devices_snapshot:
            device_index = device.get("index", 0)
            channels: List[str] = [channel.strip() for channel in device.get("channels", [])]

            # Basic protection
            if num_poles <= 0:
                continue

            expected_min_len = 2 * num_poles  # Terminals
            # body: rest
            body_names = getattr(data, "other_measures_names", [])
            # If a channel is missing, fill with empty strings
            if len(channels) < expected_min_len + len(body_names):
                channels = channels + [""] * (expected_min_len + len(body_names) - len(channels))

            # 3.1) poles_channels
            poles_channels: List[Dict[str, Any]] = []
            for pole_idx in range(num_poles):
                upper_idx = 2 * pole_idx
                lower_idx = 2 * pole_idx + 1

                upper_side = channels[upper_idx] if upper_idx < len(channels) else ""
                lower_side = channels[lower_idx] if lower_idx < len(channels) else ""

                poles_channels.append(
                    {
                        "pole_number": pole_idx + 1,
                        "upper_side": upper_side,
                        "lower_side": lower_side,
                    }
                )

            # 3.2) body_channels
            body_channels: Dict[str, str] = {}
            base_body_idx = 2 * num_poles
            for offset, name in enumerate(body_names):
                idx = base_body_idx + offset
                body_channels[name] = channels[idx] if idx < len(channels) else ""

            connected_channels.append(
                {
                    "device": device_index,
                    "poles_channels": poles_channels,
                    "body_channels": body_channels,
                }
            )

        circuit_breakers = {
            "number_of_devices": num_devices,
            "number_of_poles": num_poles,
            "connected_channels": connected_channels,
        }

        # 4) Limiters
        limits_snapshot: List[Dict[str, str]] = snapshot.get("limits", [])

        limits_dict: Dict[str, float] = {}
        for item in limits_snapshot:
            name = (item.get("name") or "").strip()
            value_str = (item.get("value") or "").strip()

            if not name or not value_str:
                continue

            try:
                value = float(value_str.replace(",", "."))  # aceita vírgula decimal
            except ValueError:
                continue

            limits_dict[name] = value

        limiters = {
            "number_of_limiters": len(limits_dict),
            "limits": limits_dict,
        }

        # 5) Mount final payload
        payload = {
            "file_directory": file_directory,
            "ambient": ambient,
            "circuit_breakers": circuit_breakers,
            "nicknames": {},  # for now 
            "limiters": limiters,
        }

        return payload

    def ask_queue_to_validate(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:

        # Get the payload
        payload = self.snapshot_to_worker_payload(snapshot=snapshot)

        # Update the user_input_variables
        data.user_input_variables = {
            "target": "worker",
            "job": "validate_inputs",
            "payload": payload
        }

        # Insert in the worker queue
        data.data_queue.put(data.user_input_variables)

        return data.user_input_variables