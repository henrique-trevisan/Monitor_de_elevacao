test_snapshot = {
    'file_path': r'Q:/GROUPS/BR_SC_JGS_WA_TECNICO/LAB_WAU/USUÁRIOS/Vitória/Elevação de temperatura/Dados dos registradores/14.11/Data 11_13_2025 07_11_53 1.csv',
    'ambient': {
        'channels': ['ch01', 'ch02']
        },
    'num_devices': 2,
    'num_poles': 3,
    'devices': [
        {
            'index': 1,
            'channels': ['ch03', 'ch04', 'ch05', 'ch06', 'ch07', 'ch10', 'ch11', 'ch12', 'ch13', 'ch14']
        },
        {
            'index': 2,
            'channels': ['ch15', 'ch16', 'ch17', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25', 'ch26']
        }
    ],
    'limits': [
        {
            'name': 'Left side',
            'value': '60'
        },
        {
            'name': 'Right side',
            'value': '60'
        },
        {
            'name': 'Front',
            'value': '50'
        },
        {
            'name': 'Handle',
            'value': '40'
        }
    ]
}


# Import
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from monitor_de_elevacao.infra.config_adapter import ConfigAdapter
import json

config_adapter = ConfigAdapter()

payload = config_adapter.snapshot_to_worker_payload(test_snapshot)
queue_payload = config_adapter.ask_queue_to_validate(test_snapshot)

print(json.dumps(queue_payload, indent=2, ensure_ascii=False))