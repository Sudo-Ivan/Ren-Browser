"""Settings interface for Ren Browser.

Provides configuration management, log viewing, and storage
information display.
"""

import flet as ft

from ren_browser.logs import ERROR_LOGS, RET_LOGS
from ren_browser.storage.storage import get_storage_manager


def open_settings_tab(page: ft.Page, tab_manager):
    """Open a settings tab with configuration and debugging options.

    Args:
        page: Flet page instance for UI updates.
        tab_manager: Tab manager to add the settings tab to.

    """
    storage = get_storage_manager(page)

    try:
        config_text = storage.load_config()
    except Exception as ex:
        config_text = f"Error reading config: {ex}"

    config_field = ft.TextField(
        label="Reticulum config",
        value=config_text,
        expand=True,
        multiline=True,
    )

    def on_save_config(ev):
        try:
            success = storage.save_config(config_field.value)
            if success:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Config saved successfully. Please restart the app."),
                    open=True,
                )
            else:
                page.snack_bar = ft.SnackBar(
                    ft.Text("Error saving config: Storage operation failed"), open=True
                )
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                ft.Text(f"Error saving config: {ex}"), open=True
            )
        page.update()

    save_btn = ft.ElevatedButton("Save and Restart", on_click=on_save_config)
    error_field = ft.TextField(
        label="Error Logs",
        value="",
        expand=True,
        multiline=True,
        read_only=True,
    )
    ret_field = ft.TextField(
        label="Reticulum logs",
        value="",
        expand=True,
        multiline=True,
        read_only=True,
    )

    # Storage information for debugging
    storage_info = storage.get_storage_info()
    storage_text = "\n".join([f"{key}: {value}" for key, value in storage_info.items()])
    storage_field = ft.TextField(
        label="Storage Information",
        value=storage_text,
        expand=True,
        multiline=True,
        read_only=True,
    )

    content_placeholder = ft.Container(expand=True)

    def show_config(ev):
        content_placeholder.content = config_field
        page.update()

    def show_errors(ev):
        error_field.value = "\n".join(ERROR_LOGS) or "No errors logged."
        content_placeholder.content = error_field
        page.update()

    def show_ret_logs(ev):
        ret_field.value = "\n".join(RET_LOGS) or "No Reticulum logs."
        content_placeholder.content = ret_field
        page.update()

    def show_storage_info(ev):
        storage_info = storage.get_storage_info()
        storage_field.value = "\n".join(
            [f"{key}: {value}" for key, value in storage_info.items()]
        )
        content_placeholder.content = storage_field
        page.update()

    def refresh_current_view(ev):
        # Refresh the currently displayed content
        if content_placeholder.content == error_field:
            show_errors(ev)
        elif content_placeholder.content == ret_field:
            show_ret_logs(ev)
        elif content_placeholder.content == storage_field:
            show_storage_info(ev)
        elif content_placeholder.content == config_field:
            show_config(ev)

    btn_config = ft.ElevatedButton("Config", on_click=show_config)
    btn_errors = ft.ElevatedButton("Errors", on_click=show_errors)
    btn_ret = ft.ElevatedButton("Ret Logs", on_click=show_ret_logs)
    btn_storage = ft.ElevatedButton("Storage", on_click=show_storage_info)
    btn_refresh = ft.ElevatedButton("Refresh", on_click=refresh_current_view)
    button_row = ft.Row(
        controls=[btn_config, btn_errors, btn_ret, btn_storage, btn_refresh]
    )
    content_placeholder.content = config_field
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
