import threading
from .ui.tray import create_tray_icon
from monitor_de_elevacao.ui.gui import App

def run():

    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()
    
    app = App()
