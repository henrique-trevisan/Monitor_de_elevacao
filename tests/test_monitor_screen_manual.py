# tests/test_monitor_screen_manual.py

import sys
from pathlib import Path

# -------------------------------------------------------------------
# Ajusta o sys.path para conseguir importar o pacote do projeto
# -------------------------------------------------------------------
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

import customtkinter as ctk  # type: ignore

from monitor_de_elevacao.ui.monitor_screen import MonitorScreen
from monitor_de_elevacao.infra import data


# -------------------------------------------------------------------
# Helpers para construir payloads de teste
# -------------------------------------------------------------------

def build_fake_snapshot() -> dict:
    """
    Snapshot mínimo só para o MonitorScreen.on_show() não quebrar.
    """
    return {
        "file_path": r"C:\fake\example.csv",
        "ambient": {
            "channels": ["ch01", "ch02"],
        },
        "num_devices": 2,
        "num_poles": 2,
        "devices": [],
        "limits": [],
    }


def build_fake_monitor_payload() -> dict:
    """
    Payload de monitoramento com:
      - 6 linhas de ambiente (t1, t2, mean)
      - 2 dispositivos, 4 colunas cada
    Compatível com o que MonitorScreen.update_from_payload espera.
    """

    # 1) Ambiente: 6 amostras
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

    # 2) Dispositivos: mesmo número de colunas para readings/deltas/result
    column_labels = ["Upper pole 1", "Lower pole 1", "Left side", "Handle"]
    n_cols = len(column_labels)

    def make_device(device_index: int, offset: float) -> dict:
        readings: list[list[float]] = []
        deltas: list[list[float]] = []

        # Usa a média ambiente só para gerar números coerentes
        for i, row in enumerate(ambient_rows):
            mean = row["mean"]

            # Cria temperaturas artificiais para cada coluna
            r_row: list[float] = []
            d_row: list[float] = []
            for j in range(n_cols):
                temp = mean + 10.0 + offset + j + 0.1 * i
                r_row.append(temp)
                d_row.append(temp - mean)
            readings.append(r_row)
            deltas.append(d_row)

        # Calcula max/min/estab por coluna a partir dos deltas
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

    monitor_payload = {
        "update_index": 1,
        "ambient": {
            "rows": ambient_rows,
            "stats": ambient_stats,
        },
        "devices": devices_payload,
        # "limits": [...]  # vai ser usado depois; por ora é opcional
    }

    return monitor_payload


# -------------------------------------------------------------------
# Função principal de teste manual
# -------------------------------------------------------------------

def main() -> None:
    # Configuração básica do customtkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("MonitorScreen manual test")
    root.geometry("1200x800")

    # Prepara o "controller" mínimo que a MonitorScreen espera
    class DummyController:
        def show_frame(self, name: str) -> None:
            print(f"DummyController.show_frame({name}) called")

    controller = DummyController()

    # Cria a tela de monitoramento
    screen = MonitorScreen(parent=root, controller=controller)
    screen.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Deixa o sistema em modo "monitoring" para o LED piscar
    data.monitoring = True

    # Snapshot mínimo só para o on_show() montar o resumo
    data.last_config_snapshot = build_fake_snapshot()

    # Chama o hook de exibição
    screen.on_show()

    # Agenda a atualização com o payload fake
    fake_payload = build_fake_monitor_payload()
    # usa after só para simular a ideia de "chegou algo pela fila"
    root.after(500, lambda: screen.update_from_payload(fake_payload))

    root.mainloop()


if __name__ == "__main__":
    main()
