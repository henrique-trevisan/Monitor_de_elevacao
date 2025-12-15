# device_monitor_tables.py
from typing import List, Any
import customtkinter as ctk

class DeviceDataTable(ctk.CTkFrame):
    """
    Tabela read-only para um dispositivo (leituras ou deltas).
    Linha 0: cabeçalho ["Sample", *column_labels]
    Linhas 1..max_rows: valores.
    """

    def __init__(self, parent: ctk.CTkFrame, column_labels: List[str], max_rows: int = 6) -> None:
        super().__init__(parent)

        self.max_rows = max_rows
        self.column_labels = column_labels

        # Número total de colunas = 1 (índice) + nº de medições
        num_cols = 1 + len(column_labels)
        for col in range(num_cols):
            self.grid_columnconfigure(col, weight=1)

        # Cabeçalho
        headers = ["Sample"] + column_labels
        self.cells: List[List[ctk.CTkLabel]] = []

        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(self, text=text, font=("Arial", 13, "bold"))
            lbl.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        # Linhas de dados
        for row in range(1, self.max_rows + 1):
            row_cells: List[ctk.CTkLabel] = []

            # Índice da amostra
            lbl_index = ctk.CTkLabel(self, text=str(row))
            lbl_index.grid(row=row, column=0, padx=4, pady=2, sticky="nsew")
            row_cells.append(lbl_index)

            # Colunas de valores
            for col in range(1, num_cols):
                lbl_val = ctk.CTkLabel(self, text="-")
                lbl_val.grid(row=row, column=col, padx=4, pady=2, sticky="nsew")
                row_cells.append(lbl_val)

            self.cells.append(row_cells)

    @staticmethod
    def format_value(value: Any) -> str:
        """
        Formata o valor com 1 casa decimal, se for numérico.
        """
        if value is None:
            return "-"

        try:
            return f"{float(value):.1f}"
        except (TypeError, ValueError):
            return str(value)

    def update_rows(self, rows: List[list[Any]]) -> None:
        """
        Atualiza as linhas da tabela.
        rows deve ser uma lista de listas: cada sublista é uma linha com
        len(sublista) == len(self.column_labels).
        """
        for i in range(self.max_rows):
            if i < len(rows):
                row_data = rows[i]
                for col in range(1, len(self.cells[i])):  # coluna 0 é o índice
                    value = row_data[col - 1] if (col - 1) < len(row_data) else None
                    self.cells[i][col].configure(text=self.format_value(value))
            else:
                # Limpa linhas que não possuem dado
                for col in range(1, len(self.cells[i])):
                    self.cells[i][col].configure(text="-")

class DeviceResultTable(ctk.CTkFrame):
    """
    Tabela para mostrar Max / Min / Estab por coluna.
    Linha 0: cabeçalho ["", *column_labels]
    Linha 1: Max
    Linha 2: Min
    Linha 3: Estab
    """

    def __init__(self, parent: ctk.CTkFrame, column_labels: List[str]) -> None:
        super().__init__(parent)

        self.column_labels = column_labels

        num_cols = 1 + len(column_labels)
        for col in range(num_cols):
            self.grid_columnconfigure(col, weight=1)

        # Cabeçalho
        headers = [""] + column_labels
        for col, text in enumerate(headers):
            lbl = ctk.CTkLabel(self, text=text, font=("Arial", 13, "bold"))
            lbl.grid(row=0, column=col, padx=4, pady=4, sticky="nsew")

        row_names = ["Max", "Min", "Estab"]
        self.value_labels: List[List[ctk.CTkLabel]] = []

        for row_idx, name in enumerate(row_names, start=1):
            lbl_name = ctk.CTkLabel(self, text=name)
            lbl_name.grid(row=row_idx, column=0, padx=4, pady=2, sticky="w")

            row_vals: List[ctk.CTkLabel] = []
            for col in range(1, num_cols):
                lbl_val = ctk.CTkLabel(self, text="-")
                lbl_val.grid(row=row_idx, column=col, padx=4, pady=2, sticky="nsew")
                row_vals.append(lbl_val)

            self.value_labels.append(row_vals)

    @staticmethod
    def format_value(value: Any) -> str:
        if value is None:
            return "-"
        try:
            return f"{float(value):.1f}"
        except (TypeError, ValueError):
            return str(value)

    def update_result(
        self,
        max_values: list[Any] | None,
        min_values: list[Any] | None,
        estab_values: list[Any] | None,
    ) -> None:
        """
        Atualiza as 3 linhas de resultado com listas numéricas.
        Cada lista deve ter o mesmo tamanho de column_labels.
        """
        rows_data = [max_values or [], min_values or [], estab_values or []]

        for row_idx, row_data in enumerate(rows_data):
            for col_idx in range(len(self.value_labels[row_idx])):
                value = row_data[col_idx] if col_idx < len(row_data) else None
                self.value_labels[row_idx][col_idx].configure(
                    text=self.format_value(value)
                )

class DeviceMonitorGroup(ctk.CTkFrame):
    """
    Agrupa as 3 tabelas de um dispositivo:
        - Leituras
        - Deltas
        - Resultado (Max/Min/Estab)
    """

    def __init__(
        self,
        parent: ctk.CTkFrame,
        device_index: int,
        column_labels: List[str],
        max_rows: int = 6,
    ) -> None:
        super().__init__(parent)

        self.device_index = device_index
        self.column_labels = column_labels

        self.grid_columnconfigure(0, weight=1)

        # Título do dispositivo
        title = ctk.CTkLabel(
            self,
            text=f"Device #{device_index}",
            font=("Arial", 16, "bold"),
        )
        title.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))

        # Tabela de leituras
        lbl_readings = ctk.CTkLabel(self, text="Readings [°C]")
        lbl_readings.grid(row=1, column=0, sticky="w", padx=5, pady=(5, 2))

        self.readings_table = DeviceDataTable(self, column_labels, max_rows=max_rows)
        self.readings_table.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Tabela de deltas
        lbl_deltas = ctk.CTkLabel(self, text="Deltas [ΔT = Tchannel − Tmean ambient]")
        lbl_deltas.grid(row=3, column=0, sticky="w", padx=5, pady=(5, 2))

        self.deltas_table = DeviceDataTable(self, column_labels, max_rows=max_rows)
        self.deltas_table.grid(row=4, column=0, sticky="ew", padx=5, pady=(0, 5))

        # Tabela de resultado
        lbl_result = ctk.CTkLabel(self, text="Result (Max / Min / Estab of ΔT)")
        lbl_result.grid(row=5, column=0, sticky="w", padx=5, pady=(5, 2))

        self.result_table = DeviceResultTable(self, column_labels)
        self.result_table.grid(row=6, column=0, sticky="ew", padx=5, pady=(0, 10))

    def update_from_payload(self, device_payload: dict) -> None:
        """
        Atualiza as 3 tabelas usando o payload do dispositivo.
        Espera chaves: "readings", "deltas" e "result" com
        "max", "min", "estab".
        """
        readings = device_payload.get("readings", [])
        deltas = device_payload.get("deltas", [])
        result = device_payload.get("result", {})

        self.readings_table.update_rows(readings)
        self.deltas_table.update_rows(deltas)
        self.result_table.update_result(
            max_values=result.get("max"),
            min_values=result.get("min"),
            estab_values=result.get("estab"),
        )
