import argparse
import subprocess
import sys
import pathlib
import datetime

import flet as ft
from flet import AppView, Page

from ren_browser.ui.ui import build_ui

# Current renderer name
RENDERER = "plaintext"

ERROR_LOGS: list[str] = []

def log_error(msg: str):
    timestamp = datetime.datetime.now().isoformat()
    ERROR_LOGS.append(f"[{timestamp}] {msg}")

async def main(page: Page):
    # Build the main UI layout
    build_ui(page)

def run():
    global RENDERER
    parser = argparse.ArgumentParser(description="Ren Browser")
    parser.add_argument("-r", "--renderer", choices=["plaintext", "micron"], default=RENDERER, help="Select renderer (plaintext or micron)")
    parser.add_argument("-w", "--web", action="store_true", help="Launch in web browser mode")
    parser.add_argument("-p", "--port", type=int, default=None, help="Port for web server")
    args = parser.parse_args()
    RENDERER = args.renderer

    if args.web:
        # Run web mode on optional fixed port
        if args.port is not None:
            ft.app(main, view=AppView.WEB_BROWSER, port=args.port)
        else:
            ft.app(main, view=AppView.WEB_BROWSER)
    else:
        ft.app(main)

if __name__ == "__main__":
    run()

def web():
    """Launch Ren Browser in web mode via Flet CLI."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", str(script_path), "--web"])
    sys.exit(rc)

def android():
    """Launch Ren Browser in Android mode via Flet CLI."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", str(script_path), "--android"])
    sys.exit(rc)

def ios():
    """Launch Ren Browser in iOS mode via Flet CLI."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", str(script_path), "--ios"])
    sys.exit(rc)

# Hot reload (dev) mode entrypoints

def run_dev():
    """Launch Ren Browser in desktop mode via Flet CLI with hot reload."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", "-d", "-r", str(script_path)])
    sys.exit(rc)

def web_dev():
    """Launch Ren Browser in web mode via Flet CLI with hot reload."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", "--web", "-d", "-r", str(script_path)])
    sys.exit(rc)

def android_dev():
    """Launch Ren Browser in Android mode via Flet CLI with hot reload."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", "--android", "-d", "-r", str(script_path)])
    sys.exit(rc)

def ios_dev():
    """Launch Ren Browser in iOS mode via Flet CLI with hot reload."""
    script_path = pathlib.Path(__file__).resolve()
    rc = subprocess.call(["flet", "run", "--ios", "-d", "-r", str(script_path)])
    sys.exit(rc)
