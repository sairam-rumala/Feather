import os
import sys
import time
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class RestartOnChange(FileSystemEventHandler):

    def __init__(self):
        self.process = None
        self.start_program()

    def start_program(self):
        print("Starting application...")
        self.process = subprocess.Popen([sys.executable, "main.py"])

    def restart_program(self):
        print("\nChange detected. Restarting application...")

        if self.process:
            self.process.terminate()

            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.start_program()

    def on_modified(self, event):
        if event.is_directory:
            return

        if event.src_path.endswith(".py"):
            self.restart_program()


if __name__ == "__main__":

    folder = os.path.dirname(os.path.abspath(__file__))

    event_handler = RestartOnChange()

    observer = Observer()
    observer.schedule(
        event_handler,
        folder,
        recursive=False
    )

    observer.start()

    print("Development auto-reloader is running.")
    print("Edit main.py or ui.py and save the file.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping...")

        observer.stop()

        if event_handler.process:
            event_handler.process.terminate()

    observer.join()