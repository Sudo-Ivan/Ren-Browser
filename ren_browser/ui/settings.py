import flet as ft
import pathlib
from ren_browser.app import ERROR_LOGS

def open_settings_tab(page: ft.Page, tab_manager):
    # Locate Reticulum config file
    config_path = pathlib.Path(__file__).resolve().parents[2] / "config" / "config"
    try:
        config_text = config_path.read_text()
    except Exception as ex:
        config_text = f"Error reading config: {ex}"
    # Config editor
    config_field = ft.TextField(
        label="Reticulum config",
        value=config_text,
        expand=True,
        multiline=True,
    )
    # Save button handler
    def on_save_config(ev):
        try:
            config_path.write_text(config_field.value)
            page.snack_bar = ft.SnackBar(ft.Text("Config saved. Please restart the app."), open=True)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error saving config: {ex}"), open=True)
        page.update()
    save_btn = ft.ElevatedButton("Save and Restart", on_click=on_save_config)
    # Error logs viewer
    error_text = "\n".join(ERROR_LOGS) or "No errors logged."
    error_field = ft.TextField(
        label="Error Logs",
        value=error_text,
        expand=True,
        multiline=True,
        read_only=True,
    )
    # Placeholder for content switching
    content_placeholder = ft.Container(expand=True)
    # View switch handlers
    def show_config(ev):
        content_placeholder.content = config_field
        page.update()
    def show_errors(ev):
        content_placeholder.content = error_field
        page.update()
    btn_config = ft.ElevatedButton("Config", on_click=show_config)
    btn_errors = ft.ElevatedButton("Errors", on_click=show_errors)
    button_row = ft.Row(controls=[btn_config, btn_errors])
    # Initialize to config view
    content_placeholder.content = config_field
    # Assemble settings UI
    settings_content = ft.Column(
        expand=True,
        controls=[
            button_row,
            content_placeholder,
            ft.Row([save_btn]),
        ],
    )
    tab_manager._add_tab_internal("Settings", settings_content)
    idx = len(tab_manager.manager.tabs) - 1
    tab_manager.select_tab(idx)
    page.update() 