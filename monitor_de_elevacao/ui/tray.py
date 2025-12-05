import pystray
from ..infra import data

# ---------------------------------------------
# -- System tray
# ---------------------------------------------

def on_open(icon, item):

    # Open menu or the click on the icon
    data.tray_queue.put(("show_window", None))

def on_toggle_monitoring(icon, item):
 
    # Update the mode of the GUI
    data.tray_queue.put(("toggle_monitoring", None))

def on_exit(icon, item):

    # Ask confirmation for exit
    data.tray_queue.put(("exit", None, icon))

def create_tray_icon():

    menu = pystray.Menu(
        pystray.MenuItem("Open", on_open, default=True),  # default=True -> default action (icon click)
        pystray.MenuItem(
            lambda item: "Stop monitoring" if data.monitoring else "Start monitoring",
            on_toggle_monitoring
            ),
        pystray.MenuItem("Exit", on_exit)
    )

    icon = pystray.Icon(
        "TrayCounter",
        data.icon_monitoring if data.monitoring else data.icon_awaiting,
        "Contador",
        menu
    )

    data.icon = icon

    icon.run()