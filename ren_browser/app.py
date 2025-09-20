"""Ren Browser main application module.

This module provides the entry point and platform-specific launchers for the
Ren Browser, a browser for the Reticulum Network built with Flet.
"""
import argparse

import flet as ft
import RNS
from flet import AppView, Page

from ren_browser.storage.storage import initialize_storage
from ren_browser.ui.ui import build_ui

RENDERER = "plaintext"
RNS_CONFIG_DIR = None

async def main(page: Page):
    """Initialize and launch the Ren Browser application.

    Sets up the loading screen, initializes Reticulum network,
    and builds the main UI.
    """
    loader = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        content=ft.Column(
            [ft.ProgressRing(), ft.Text("Initializing reticulum network")],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
    page.add(loader)
    page.update()

    def init_ret():
        # Initialize storage system
        storage = initialize_storage(page)

        # Get Reticulum config directory
        if RNS_CONFIG_DIR:
            config_dir = RNS_CONFIG_DIR
        else:
            config_dir = storage.get_reticulum_config_path()
        try:
            # Set up logging capture first, before RNS init
            import ren_browser.logs
            ren_browser.logs.setup_rns_logging()
            RNS.Reticulum(str(config_dir))
        except (OSError, ValueError):
            pass
        page.controls.clear()
        build_ui(page)
        page.update()

    page.run_thread(init_ret)

def run():
    """Run Ren Browser with command line argument parsing."""
    global RENDERER, RNS_CONFIG_DIR
    parser = argparse.ArgumentParser(description="Ren Browser")
    parser.add_argument("-r", "--renderer", choices=["plaintext", "micron"], default=RENDERER, help="Select renderer (plaintext or micron)")
    parser.add_argument("-w", "--web", action="store_true", help="Launch in web browser mode")
    parser.add_argument("-p", "--port", type=int, default=None, help="Port for web server")
    parser.add_argument("-c", "--config-dir", type=str, default=None, help="RNS config directory (default: ~/.reticulum/)")
    args = parser.parse_args()
    RENDERER = args.renderer

    # Set RNS config directory
    if args.config_dir:
        RNS_CONFIG_DIR = args.config_dir
    else:
        import pathlib
        RNS_CONFIG_DIR = str(pathlib.Path.home() / ".reticulum")

    if args.web:
        if args.port is not None:
            ft.app(main, view=AppView.WEB_BROWSER, port=args.port)
        else:
            ft.app(main, view=AppView.WEB_BROWSER)
    else:
        ft.app(main)

if __name__ == "__main__":
    run()

def web():
    """Launch Ren Browser in web mode."""
    ft.app(main, view=AppView.WEB_BROWSER)

def android():
    """Launch Ren Browser in Android mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)

def ios():
    """Launch Ren Browser in iOS mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)

def run_dev():
    """Launch Ren Browser in desktop mode."""
    ft.app(main)

def web_dev():
    """Launch Ren Browser in web mode."""
    ft.app(main, view=AppView.WEB_BROWSER)

def android_dev():
    """Launch Ren Browser in Android mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)

def ios_dev():
    """Launch Ren Browser in iOS mode."""
    ft.app(main, view=AppView.FLET_APP_WEB)
