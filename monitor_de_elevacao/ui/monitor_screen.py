import customtkinter as ctk
from ..infra import data

class MonitorScreen(ctk.CTkFrame):

    def __init__(self, parent: ctk.CTkFrame, controller) -> None:

        super().__init__(parent)
        self.controller = controller

        title = ctk.CTkLabel(self, text="Monitor screen", font=("Arial", 24))
        title.pack(pady=20)


        info = ctk.CTkLabel(
            self,
            text=(
                "Aqui depois vão aparecer:\n"
                "- Tabelas espelhando a configuração (quantidade/colunas)\n"
                "- Cards de limites com valor lido\n"
                "- Tudo em modo somente leitura\n"
            ),
            justify="left",
        )
        info.pack(pady=10)

        btn_go_config = ctk.CTkButton(
            self,
            text="Stop monitoring",
            command=lambda: controller.show_frame("ConfigScreen"),
        )
        btn_go_config.pack(pady=20, side="bottom")