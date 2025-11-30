"""Ren Browser main application module.

This module provides the entry point and platform-specific launchers for the
Ren Browser, a browser for the Reticulum Network built with Flet.
"""

import argparse
import os
from pathlib import Path

import flet as ft
import RNS
from flet import AppView, Page

from ren_browser import rns
from ren_browser.storage.storage import initialize_storage
from ren_browser.ui.ui import build_ui

RENDERER = "plaintext"
RNS_CONFIG_DIR = None
RNS_INSTANCE = None


async def main(page: Page):
    """Initialize and launch the Ren Browser application.

    Sets up the loading screen, initializes Reticulum network,
    and builds the main UI.
    """
    page.title = "Ren Browser"
    page.theme_mode = ft.ThemeMode.DARK

    loader = ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        bgcolor=ft.Colors.SURFACE,
        content=ft.Column(
            [
                ft.ProgressRing(color=ft.Colors.PRIMARY, width=50, height=50),
                ft.Container(height=20),
                ft.Text(
                    "Initializing Reticulum Network...",
                    size=16,
                    color=ft.Colors.ON_SURFACE,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
    )
    page.add(loader)
    page.update()

    initialize_storage(page)

    config_override = RNS_CONFIG_DIR

    print("Initializing Reticulum Network...")
    try:
        import ren_browser.logs

        ren_browser.logs.setup_rns_logging()
    except Exception:
        pass

    success = rns.initialize_reticulum(config_override)
    if not success:
        error_text = rns.get_last_error() or "Unknown error"
        print(f"Error initializing Reticulum: {error_text}")
    else:
        global RNS_INSTANCE
        RNS_INSTANCE = rns.get_reticulum_instance()
        config_dir = rns.get_config_path()
        if config_dir:
            config_path = Path(config_dir)
            print(f"RNS config directory: {config_path}")
            print(f"Config directory exists: {config_path.exists()}")
            print(
                "Config directory is writable: "
                f"{config_path.is_dir() and os.access(config_path, os.W_OK)}",
            )
        print("RNS initialized successfully")

    page.controls.clear()
    build_ui(page)
    page.update()


async def reload_reticulum(page: Page, on_complete=None):
    """Hot reload Reticulum with updated configuration.

    Args:
        page: Flet page instance
        on_complete: Optional callback to run when reload is complete

    """
    import asyncio

    try:
        global RNS_INSTANCE

        if RNS_INSTANCE:
            try:
                RNS_INSTANCE.exit_handler()
                print("RNS exit handler completed")
            except Exception as e:
                print(f"Warning during RNS shutdown: {e}")

            rns.shutdown_reticulum()
            RNS.Reticulum._Reticulum__instance = None
            RNS.Transport.destinations = []
            RNS_INSTANCE = None
            print("RNS instance cleared")

        await asyncio.sleep(0.5)

        success = rns.initialize_reticulum(RNS_CONFIG_DIR)
        if success:
            RNS_INSTANCE = rns.get_reticulum_instance()
            if on_complete:
                on_complete(True, None)
        else:
            error_text = rns.get_last_error() or "Unknown error"
            print(f"Error reinitializing Reticulum: {error_text}")
            if on_complete:
                on_complete(False, error_text)

    except Exception as e:
        print(f"Error during reload: {e}")
        if on_complete:
            on_complete(False, str(e))


def run():
    """Run Ren Browser with command line argument parsing."""
    global RENDERER, RNS_CONFIG_DIR
    parser = argparse.ArgumentParser(description="Ren Browser")
    parser.add_argument(
        "-r",
        "--renderer",
        choices=["plaintext", "micron"],
        default=RENDERER,
        help="Select renderer (plaintext or micron)",
    )
    parser.add_argument(
        "-w",
        "--web",
        action="store_true",
        help="Launch in web browser mode",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=None,
        help="Port for web server",
    )
    parser.add_argument(
        "-c",
        "--config-dir",
        type=str,
        default=None,
        help="RNS config directory (default: ~/.reticulum/)",
    )
    args = parser.parse_args()
    RENDERER = args.renderer

    # Set RNS config directory
    if args.config_dir:
        RNS_CONFIG_DIR = args.config_dir
    else:
        RNS_CONFIG_DIR = None

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
