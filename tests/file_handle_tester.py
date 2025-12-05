import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from monitor_de_elevacao.infra.file_handler import open_data_file, find_header, verify_file_existence
from monitor_de_elevacao.infra import data

data.file_path = r"C:\Users\htrevisan\OneDrive - WEG EQUIPAMENTOS ELETRICOS S.A\FILES\VSCode_Workspace\Monitor_de_elevacao\Data 11_13_2025 07_11_53 1.csv"

print(verify_file_existence())
# csv_file = open_data_file(file_path, find_header(file_path, "Scan"))
# print(csv_file['status'])
# print(csv_file['body'].head())
