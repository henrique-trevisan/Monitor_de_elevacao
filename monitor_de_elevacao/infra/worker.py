from . import data
from .file_handler import verify_file_existence, find_header, open_data_file

from time import sleep

def update_header_row():
    data.header_row = find_header(data.file_path, data.header_name)

def open_file() -> dict:
    data_file = open_data_file(data.file_path, data.header_row)
    if data_file['status'] == 'fail':
        sleep(3)  # If fail to open, wait 3 seconds and try again
        data_file = open_data_file(data.file_path, data.header_row)
    return data_file
