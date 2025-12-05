from pathlib import Path
from PIL import Image
import queue

# ---------------------------------------------
# -- Global variables
# ---------------------------------------------

# GUI variables
user_input_variables: dict = {
    "target": "worker",
    "job": "validate_inputs",
    "payload": {
        "file_directory": "C:\\testFile.csv",
        "ambient": {
            "ambient_number": 2,
            "ambient_channels": ["ch01", "ch02"]
        },
        "circuit_breakers": {
            "number_of_devices": 2,
            "number_of_poles": 1,
            "connected_channels": [
                {
                    "device": 1,
                    "poles_channels": [
                        {
                            "pole_number": 1,
                            "upper_side": "ch03",
                            "lower_side": "ch04"
                        }
                    ],
                    "body_channels": {
                        "left_side": "ch05",
                        "right_side": "ch06",
                        "front": "ch07",
                        "handle": "ch11"
                    }
                },
                {
                    "device": 2,
                    "poles_channels": [
                        {
                            "pole_number": 1,
                            "upper_side": "ch12",
                            "lower_side": "ch13"
                        }
                    ],
                    "body_channels": {
                        "left_side": "ch14",
                        "right_side": "ch15",
                        "front": "ch16",
                        "handle": "ch17"
                    }
                }
            ]
        },
        "nicknames": {
            "ch01": "temp01",
            "ch02": "temp02",
            "ch03": "Term. Sup. Pol 1",
            "ch04": "Term. Inf. Pol 1",
            "ch05": "Lateral Esquerda",
            "ch06": "Lateral Direita",
            "ch07": "Frontal",
            "ch11": "Manopla",
            "ch12": "Term. Sup. Pol 1",
            "ch13": "Term. Inf. Pol 1",
            "ch14": "Lateral Esquerda",
            "ch15": "Lateral Direita",
            "ch16": "Frontal",
            "ch17": "Manopla",
        },
        "limiters": {
            "number_of_limiters": 3,
            "limits": {
                "Frontal": 50,
                "Manopla": 60,
                "Lateral Esquerda": 45
            }
        }
    }
}

# Control variables
monitoring = False
file_path = None
file_exists = None
header_name = "Scan"
header_row = None
worker_stop = False

# Threads communication
data_queue = queue.Queue()
tray_queue = queue.Queue()
worker_thread = None
worker_stop = False
icon = None

# Icon images
# This file directory (monitor_tray/core/state.py)
PACKAGE_DIR = Path(__file__).resolve().parent
# Project package directory (one level above)
APP_DIR = PACKAGE_DIR.parent
# Root project directory (two levels above)
BASE_DIR = APP_DIR.parent
# Assets directory
ASSETS_DIR = BASE_DIR / "assets"
icon_monitoring = Image.open(ASSETS_DIR / 'icon_monitoring.png')
icon_awaiting = Image.open(ASSETS_DIR / 'icon_awaiting.png')