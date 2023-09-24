import time
import click
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class JMCWatchdog(FileSystemEventHandler):
    def __init__(self):
        self.compilation_needed = False

    def on_any_event(self, event):
        if not self.compilation_needed and event.src_path.endswith('.jmc'):
            compile_result = subprocess.run(['powershell', '-Command', 'jmc compile'], capture_output=True, text=True)
            print(compile_result.stdout)
            self.compilation_needed = True

@click.command()
def main():
    """Watch for changes in .jmc files and compile them."""
    event_handler = JMCWatchdog()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            event_handler.compilation_needed = False
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()

