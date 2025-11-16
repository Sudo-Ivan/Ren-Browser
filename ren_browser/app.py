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

    def init_ret():
        import time

        time.sleep(0.5)

        # Initialize storage system
        storage = initialize_storage(page)

        # Get Reticulum config directory from storage manager
        config_dir = storage.get_reticulum_config_path()

        # Update the global RNS_CONFIG_DIR so RNS uses the right path
        global RNS_CONFIG_DIR
        RNS_CONFIG_DIR = str(config_dir)

        # Ensure any saved config is written to filesystem before RNS init
        try:
            saved_config = storage.load_config()
            if saved_config and saved_config.strip():
                config_file_path = config_dir / "config"
                config_file_path.parent.mkdir(parents=True, exist_ok=True)
                config_file_path.write_text(saved_config, encoding="utf-8")
        except Exception as e:
            print(f"Warning: Failed to write config file: {e}")

        try:
            # Set up logging capture first, before RNS init
            import ren_browser.logs

            ren_browser.logs.setup_rns_logging()
            global RNS_INSTANCE
            RNS_INSTANCE = RNS.Reticulum(str(config_dir))
        except (OSError, ValueError):
            pass
        page.controls.clear()
        build_ui(page)
        page.update()

    page.run_thread(init_ret)


def reload_reticulum(page: Page, on_complete=None):
    """Hot reload Reticulum with updated configuration.
    
    Args:
        page: Flet page instance
        on_complete: Optional callback to run when reload is complete
    
    """
    def reload_thread():
        import time
        
        try:
            global RNS_INSTANCE
            
            if RNS_INSTANCE:
                try:
                    RNS_INSTANCE.exit_handler()
                    print("RNS exit handler completed")
                except Exception as e:
                    print(f"Warning during RNS shutdown: {e}")
                
                RNS.Reticulum._Reticulum__instance = None
                
                RNS.Transport.destinations = []
                
                RNS_INSTANCE = None
                print("RNS instance cleared")
            
            time.sleep(0.5)
            
            # Initialize storage system
            storage = initialize_storage(page)
            
            # Get Reticulum config directory from storage manager
            config_dir = storage.get_reticulum_config_path()
            
            # Ensure any saved config is written to filesystem before RNS init
            try:
                saved_config = storage.load_config()
                if saved_config and saved_config.strip():
                    config_file_path = config_dir / "config"
                    config_file_path.parent.mkdir(parents=True, exist_ok=True)
                    config_file_path.write_text(saved_config, encoding="utf-8")
            except Exception as e:
                print(f"Warning: Failed to write config file: {e}")
            
            try:
                # Re-initialize Reticulum
                import ren_browser.logs
                ren_browser.logs.setup_rns_logging()
                RNS_INSTANCE = RNS.Reticulum(str(config_dir))
                
                # Success
                if on_complete:
                    on_complete(True, None)
                    
            except Exception as e:
                print(f"Error reinitializing Reticulum: {e}")
                if on_complete:
                    on_complete(False, str(e))
                    
        except Exception as e:
            print(f"Error during reload: {e}")
            if on_complete:
                on_complete(False, str(e))
    
    page.run_thread(reload_thread)


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
        "-w", "--web", action="store_true", help="Launch in web browser mode",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=None, help="Port for web server",
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
