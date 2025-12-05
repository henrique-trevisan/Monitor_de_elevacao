import pandas as pd
import csv
import os

from . import data

def verify_file_existence() -> bool:
    if os.path.exists(data.file_path):
        data.file_exists = True
        return True
    else:
        data.file_exists = False
        return False

def _detect_encoding(file_path: str) -> str:
    """Simple BOM-based encoding detection with sensible fallback."""
    with open(file_path, "rb") as f:
        start = f.read(4)
    if start.startswith(b'\xef\xbb\xbf'):
        return "utf-8-sig"
    if start.startswith(b'\xff\xfe\x00\x00') or start.startswith(b'\x00\x00\xfe\xff'):
        return "utf-32"
    if start.startswith(b'\xff\xfe') or start.startswith(b'\xfe\xff'):
        return "utf-16"
    return "utf-8"

def find_header(file_path: str, header_name: str) -> int:
    with open(file_path, "r", encoding=_detect_encoding(file_path), newline="") as f:
        for row_idx, row in enumerate(csv.reader(f, delimiter="\t")):
            if row and row[0].strip() == header_name:
                return row_idx
    return -1

def open_data_file(file_path: str, header_row: int = None) -> dict:
    
    message = {
        'status': 'fail',
        'body': ""
    }

    try:
        file = pd.read_csv(file_path, encoding=_detect_encoding(file_path), header=header_row, sep="\t")
        message = {
            'status': 'success',
            'body': file
        }

    except FileNotFoundError:
        message['body'] = f"File not found: {file_path}"
    except pd.errors.EmptyDataError:
        message['body'] = f"CSV is empty: {file_path}"
    except pd.errors.ParserError:
        message['body'] = f"CSV parse error in {file_path}"

    return message