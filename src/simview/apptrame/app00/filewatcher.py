import asyncio
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    active_watchdog = True
except:
    active_watchdog = False
    print("Watchdog not installed so skipping the auto monitoring")


def start_monitoring(server):
    state, ctrl = server.state, server.controller

    if not active_watchdog:
        return None

    server.hot_reload = True
    current_event_loop = asyncio.get_event_loop()

    def update_ui():
        with server.state:
            ctrl.update_ui()

    class UpdateUIOnChange(FileSystemEventHandler):
        def on_modified(self, event):
            current_event_loop.call_soon_threadsafe(update_ui)

    observer = Observer()
    observer.schedule(
        UpdateUIOnChange(), str(Path(__file__).parent.absolute()), recursive=False
    )
    observer.start()
