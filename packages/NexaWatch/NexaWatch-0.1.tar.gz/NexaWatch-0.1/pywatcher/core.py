import os
import json
import subprocess
import time
import threading
import platform
import click
from watchdog.observers import Observer
from watchdog.observers.inotify import InotifyObserver
from watchdog.events import FileSystemEventHandler
from .config import LANGUAGES

from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich import print

console = Console()

# Global setting for verbose mode
VERBOSE = False

def verbose_print(msg):
    """Print message if VERBOSE mode is enabled."""
    if VERBOSE:
        console.print(msg)

def load_config(file_name=".pywatch"):
    """Load configuration from .pywatch file if it exists."""
    if os.path.exists(file_name):
        with open(file_name, 'r') as f:
            return json.load(f)
    return {}

# Default settings
DEFAULTS = {
    'path': '.',
    'recursive': True,
    'extensions': ['.py'],
    'exclude_patterns': [],
    'delay': 1,
    'log_file': None,
    'notify': False,
    'custom_command': None
}

# Merge defaults with loaded configuration
settings = {**DEFAULTS, **load_config()}

try:
    from plyer import notification
except ImportError:
    notification = None

def send_notification(title, message):
    """Send a notification. Uses osascript on macOS and falls back to plyer on other platforms."""
    if platform.system() == "Darwin":  # macOS
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script])
    elif notification:
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5
            )
        except Exception as e:
            console.print(f"[yellow]Notification error: {e}[/yellow]")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, scripts, extensions, delay, log_file, notify, exclude_patterns, interpreter="python"):
        self.scripts = list(scripts)
        self.extensions = extensions
        self.delay = delay
        self.log_file = log_file
        self.notify = notify
        self.exclude_patterns = exclude_patterns
        self.interpreter = interpreter
        self.processes = []
        self.last_change = None
        self.lock = threading.Lock()
        self.restart_scheduled = False
        self.start_scripts()

    def start_scripts(self):
        for process in self.processes:
            process.terminate()
            process.wait()

        self.processes.clear()

        for script in self.scripts:
            console.print(f"[green]Starting: {script}[/green]")
            process = subprocess.Popen([self.interpreter, script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Threads to print output and errors
            threading.Thread(target=self.print_output, args=(process.stdout,)).start()
            threading.Thread(target=self.print_errors, args=(process.stderr,)).start()

            self.processes.append(process)

    def print_output(self, output_stream):
        for line in iter(output_stream.readline, ''):
            console.print(line.strip())
            self.log(f"[stdout] {line.strip()}")

    def print_errors(self, error_stream):
        for line in iter(error_stream.readline, ''):
            console.print(line.strip(), style='bold red')
            self.log(f"[stderr] {line.strip()}")

    def handle_event(self, event, action_desc):
        if any(pattern in event.src_path for pattern in self.exclude_patterns):
            return

        if self.extensions and not event.src_path.endswith(tuple(self.extensions)):
            return

        console.print(f"[yellow]{action_desc}: {event.src_path}[/yellow]")
        self.log(f"{action_desc}: {event.src_path}")

        with self.lock:
            self.last_change = time.time()

        if not self.restart_scheduled:
            self.restart_scheduled = True
            console.print("[yellow]Waiting for changes to stabilize...[/yellow]")
            threading.Thread(target=self.restart_after_delay).start()

    def on_modified(self, event):
        self.handle_event(event, "File modified")

    def on_created(self, event):
        self.handle_event(event, "File created")

    def on_deleted(self, event):
        self.handle_event(event, "File deleted")

    def restart_after_delay(self):
        while True:
            time.sleep(self.delay)
            with self.lock:
                last_change_elapsed = time.time() - self.last_change
                if last_change_elapsed >= self.delay:
                    break

        self.start_scripts()
        self.restart_scheduled = False

    def log(self, message):
        """Write a message to the log file."""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")

def interactive_mode(handler):
    """Listen for user commands in interactive mode."""
    while True:
        cmd = Prompt.ask("> ")
        if cmd in ["r", "restart"]:
            handler.start_scripts()
        elif cmd in ["p", "pause"]:
            handler.pause()
        elif cmd in ["res", "resume"]:
            handler.resume()
        elif cmd in ["q", "quit"]:
            console.print("[red]Exiting PyWatcher.[/red]")
            os._exit(0)  # Use os._exit to immediately terminate all threads



@click.command()
@click.argument('scripts', required=False, nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--path', '-p', default='.', help='Path to watch (default is current directory).')
@click.option('--recursive', '-r', is_flag=True, default=True, help='Recursively watch directories.')
@click.option('--extensions', '-e', multiple=True, type=str, help='File extensions to watch, e.g. ".py". Can be used multiple times.')
@click.option('--exclude-patterns', '-x', multiple=True, type=str, help='Patterns to exclude from watching. Can be used multiple times.')
@click.option('--delay', '-d', default=1, type=int, help='Delay (in seconds) between a file change detection and script restart.')
@click.option('--log-file', type=click.Path(file_okay=True, dir_okay=False, writable=True), help='Path to a log file where events will be recorded.')
@click.option('--notify', is_flag=True, help='Enable desktop notifications when the script is restarted.')
@click.option('--interpreter', '-i', default=None, help='Explicit interpreter to use.')
@click.option('--language', '-l', default='py', help='Programming language of the script. Used to determine the interpreter if not explicitly set.')
@click.option('--verbose', is_flag=True, help='Enable verbose mode.')
def pywatcher(scripts, path, recursive, extensions, exclude_patterns, delay, log_file, notify, interpreter, language, verbose):
    global VERBOSE
    VERBOSE = verbose

    if not interpreter:
        interpreter = LANGUAGES.get(language)
        if not interpreter:
            console.print(f"[red]Unsupported language: {language}[/red]")
            return

    observer = InotifyObserver()
    handler = FileChangeHandler(scripts, extensions, delay, log_file, notify, exclude_patterns, interpreter)
    observer.schedule(handler, path, recursive=recursive)
    try:
        observer.start()
        console.print(f"[blue]Watching for changes in '{path}'...[/blue]")
        threading.Thread(target=interactive_mode, args=(handler,), daemon=True).start()
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        for process in handler.processes:
            process.terminate()
        console.print("[red]Watcher stopped.[/red]")

if __name__ == "__main__":
    pywatcher()