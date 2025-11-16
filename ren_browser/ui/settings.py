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

    app_settings = storage.load_app_settings()

    config_field = ft.TextField(
        label="Reticulum Configuration",
        value=config_text,
        expand=True,
        multiline=True,
        min_lines=15,
        max_lines=20,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
        text_style=ft.TextStyle(font_family="monospace", size=12),
    )

    horizontal_scroll_switch = ft.Switch(
        label="Enable Horizontal Scroll (preserve ASCII art)",
        value=app_settings.get("horizontal_scroll", False),
    )

    page_bgcolor_field = ft.TextField(
        label="Page Background Color (hex)",
        value=app_settings.get("page_bgcolor", "#000000"),
        hint_text="#000000",
        width=200,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
    )

    color_preview = ft.Container(
        width=40,
        height=40,
        bgcolor=app_settings.get("page_bgcolor", "#000000"),
        border_radius=8,
        border=ft.border.all(1, ft.Colors.GREY_700),
    )

    def on_bgcolor_change(e):
        try:
            color_preview.bgcolor = page_bgcolor_field.value
            page.update()
        except Exception:
            pass

    page_bgcolor_field.on_change = on_bgcolor_change

    def on_save_config(ev):
        try:
            success = storage.save_config(config_field.value)
            if success:
                snack = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.GREEN_400,
                                size=20,
                            ),
                            ft.Text(
                                "Configuration saved! Restart app to apply changes.",
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        tight=True,
                    ),
                    bgcolor=ft.Colors.GREEN_900,
                    duration=3000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
            else:
                snack = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                            ft.Text(
                                "Failed to save configuration", color=ft.Colors.WHITE
                            ),
                        ],
                        tight=True,
                    ),
                    bgcolor=ft.Colors.RED_900,
                    duration=3000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
        except Exception as ex:
            snack = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                        ft.Text(f"Error: {ex}", color=ft.Colors.WHITE),
                    ],
                    tight=True,
                ),
                bgcolor=ft.Colors.RED_900,
                duration=4000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

    def on_save_and_reload_config(ev):
        try:
            success = storage.save_config(config_field.value)
            if not success:
                snack = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                            ft.Text(
                                "Failed to save configuration", color=ft.Colors.WHITE
                            ),
                        ],
                        tight=True,
                    ),
                    bgcolor=ft.Colors.RED_900,
                    duration=3000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
                return

            loading_snack = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.ProgressRing(
                            width=16,
                            height=16,
                            stroke_width=2,
                            color=ft.Colors.BLUE_400,
                        ),
                        ft.Text("Reloading Reticulum...", color=ft.Colors.WHITE),
                    ],
                    tight=True,
                ),
                bgcolor=ft.Colors.BLUE_900,
                duration=10000,
            )
            page.overlay.append(loading_snack)
            loading_snack.open = True
            page.update()

            def on_reload_complete(success, error):
                loading_snack.open = False
                page.update()

                if success:
                    snack = ft.SnackBar(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.CHECK_CIRCLE,
                                    color=ft.Colors.GREEN_400,
                                    size=20,
                                ),
                                ft.Text(
                                    "Reticulum reloaded successfully!",
                                    color=ft.Colors.WHITE,
                                ),
                            ],
                            tight=True,
                        ),
                        bgcolor=ft.Colors.GREEN_900,
                        duration=3000,
                    )
                else:
                    snack = ft.SnackBar(
                        content=ft.Row(
                            controls=[
                                ft.Icon(
                                    ft.Icons.ERROR, color=ft.Colors.RED_400, size=20
                                ),
                                ft.Text(
                                    f"Reload failed: {error}", color=ft.Colors.WHITE
                                ),
                            ],
                            tight=True,
                        ),
                        bgcolor=ft.Colors.RED_900,
                        duration=4000,
                    )
                page.overlay.append(snack)
                snack.open = True
                page.update()

            import ren_browser.app as app_module

            app_module.reload_reticulum(page, on_reload_complete)

        except Exception as ex:
            snack = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                        ft.Text(f"Error: {ex}", color=ft.Colors.WHITE),
                    ],
                    tight=True,
                ),
                bgcolor=ft.Colors.RED_900,
                duration=4000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

    def on_save_app_settings(ev):
        try:
            new_settings = {
                "horizontal_scroll": horizontal_scroll_switch.value,
                "page_bgcolor": page_bgcolor_field.value,
            }
            success = storage.save_app_settings(new_settings)
            if success:
                tab_manager.apply_settings(new_settings)
                snack = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.CHECK_CIRCLE,
                                color=ft.Colors.GREEN_400,
                                size=20,
                            ),
                            ft.Text(
                                "Appearance settings saved and applied!",
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        tight=True,
                    ),
                    bgcolor=ft.Colors.GREEN_900,
                    duration=2000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
            else:
                snack = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                            ft.Text(
                                "Failed to save appearance settings",
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        tight=True,
                    ),
                    bgcolor=ft.Colors.RED_900,
                    duration=3000,
                )
                page.overlay.append(snack)
                snack.open = True
                page.update()
        except Exception as ex:
            snack = ft.SnackBar(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400, size=20),
                        ft.Text(f"Error: {ex}", color=ft.Colors.WHITE),
                    ],
                    tight=True,
                ),
                bgcolor=ft.Colors.RED_900,
                duration=4000,
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()

    save_btn = ft.ElevatedButton(
        "Save Configuration",
        icon=ft.Icons.SAVE,
        on_click=on_save_config,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
    )

    save_reload_btn = ft.ElevatedButton(
        "Save & Hot Reload",
        icon=ft.Icons.REFRESH,
        on_click=on_save_and_reload_config,
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
    )

    save_appearance_btn = ft.ElevatedButton(
        "Save Appearance",
        icon=ft.Icons.PALETTE,
        on_click=on_save_app_settings,
        bgcolor=ft.Colors.BLUE_700,
        color=ft.Colors.WHITE,
    )
    error_field = ft.TextField(
        label="Error Logs",
        value="",
        expand=True,
        multiline=True,
        read_only=True,
        min_lines=15,
        max_lines=20,
        border_color=ft.Colors.GREY_700,
        text_style=ft.TextStyle(font_family="monospace", size=12),
    )
    ret_field = ft.TextField(
        label="Reticulum Logs",
        value="",
        expand=True,
        multiline=True,
        read_only=True,
        min_lines=15,
        max_lines=20,
        border_color=ft.Colors.GREY_700,
        text_style=ft.TextStyle(font_family="monospace", size=12),
    )

    storage_info = storage.get_storage_info()
    storage_text = "\n".join([f"{key}: {value}" for key, value in storage_info.items()])
    storage_field = ft.TextField(
        label="Storage Information",
        value=storage_text,
        expand=True,
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=15,
        border_color=ft.Colors.GREY_700,
        text_style=ft.TextStyle(font_family="monospace", size=12),
    )

    content_placeholder = ft.Container(expand=True)

    appearance_content = ft.Column(
        spacing=16,
        controls=[
            ft.Text("Appearance Settings", size=18, weight=ft.FontWeight.BOLD),
            horizontal_scroll_switch,
            ft.Row(
                controls=[
                    page_bgcolor_field,
                    color_preview,
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=16,
            ),
            save_appearance_btn,
        ],
    )

    def show_config(ev):
        content_placeholder.content = config_field
        page.update()

    def show_appearance(ev):
        content_placeholder.content = appearance_content
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
            [f"{key}: {value}" for key, value in storage_info.items()],
        )
        content_placeholder.content = storage_field
        page.update()

    def refresh_current_view(ev):
        if content_placeholder.content == error_field:
            show_errors(ev)
        elif content_placeholder.content == ret_field:
            show_ret_logs(ev)
        elif content_placeholder.content == storage_field:
            show_storage_info(ev)
        elif content_placeholder.content == appearance_content:
            show_appearance(ev)
        elif content_placeholder.content == config_field:
            show_config(ev)

    btn_config = ft.FilledButton(
        "Configuration",
        icon=ft.Icons.SETTINGS,
        on_click=show_config,
    )
    btn_appearance = ft.FilledButton(
        "Appearance",
        icon=ft.Icons.PALETTE,
        on_click=show_appearance,
    )
    btn_errors = ft.FilledButton(
        "Errors",
        icon=ft.Icons.ERROR_OUTLINE,
        on_click=show_errors,
    )
    btn_ret = ft.FilledButton(
        "Reticulum Logs",
        icon=ft.Icons.TERMINAL,
        on_click=show_ret_logs,
    )
    btn_storage = ft.FilledButton(
        "Storage",
        icon=ft.Icons.STORAGE,
        on_click=show_storage_info,
    )
    btn_refresh = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Refresh",
        on_click=refresh_current_view,
        icon_color=ft.Colors.BLUE_400,
    )

    nav_card = ft.Container(
        content=ft.Row(
            controls=[
                btn_config,
                btn_appearance,
                btn_errors,
                btn_ret,
                btn_storage,
                btn_refresh,
            ],
            spacing=8,
            wrap=True,
        ),
        padding=ft.padding.all(16),
        border_radius=12,
        bgcolor=ft.Colors.GREY_900,
    )

    content_card = ft.Container(
        content=content_placeholder,
        expand=True,
        padding=ft.padding.all(16),
        border_radius=12,
        bgcolor=ft.Colors.GREY_900,
    )

    action_row = ft.Container(
        content=ft.Row(
            controls=[save_btn, save_reload_btn],
            alignment=ft.MainAxisAlignment.END,
            spacing=8,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
    )

    content_placeholder.content = config_field
    settings_content = ft.Column(
        expand=True,
        spacing=16,
        controls=[
            ft.Container(
                content=ft.Text(
                    "Settings",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400,
                ),
                padding=ft.padding.only(left=16, top=16),
            ),
            nav_card,
            content_card,
            action_row,
        ],
    )
    tab_manager._add_tab_internal("Settings", settings_content)
    idx = len(tab_manager.manager.tabs) - 1
    tab_manager.select_tab(idx)
    page.update()
