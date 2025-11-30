"""Settings interface for Ren Browser."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import flet as ft
import RNS

from ren_browser import rns
from ren_browser.storage.storage import get_storage_manager

BUTTON_BG = "#0B3D91"
BUTTON_BG_HOVER = "#082C6C"


def _blue_button_style() -> ft.ButtonStyle:
    return ft.ButtonStyle(
        bgcolor=BUTTON_BG,
        color=ft.Colors.WHITE,
        overlay_color=BUTTON_BG_HOVER,
    )


def _get_config_file_path() -> Path:
    config_dir = rns.get_config_path()
    if config_dir:
        return Path(config_dir) / "config"
    return Path.home() / ".reticulum" / "config"


def _read_config_text(config_path: Path) -> str:
    try:
        return config_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("", encoding="utf-8")
        return ""
    except Exception as exc:  # noqa: BLE001
        return f"# Error loading config: {exc}"


def _write_config_text(config_path: Path, content: str) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(content, encoding="utf-8")


def _get_interface_statuses():
    statuses = []
    interfaces = getattr(RNS.Transport, "interfaces", []) or []
    for interface in interfaces:
        if interface is None:
            continue
        if (
            interface.__class__.__name__ == "LocalClientInterface"
            and getattr(interface, "is_connected_to_shared_instance", False)
        ):
            continue
        statuses.append(
            {
                "name": getattr(interface, "name", None) or interface.__class__.__name__,
                "online": bool(getattr(interface, "online", False)),
                "type": interface.__class__.__name__,
                "bitrate": getattr(interface, "bitrate", None),
            },
        )
    return statuses


def _format_bitrate(bitrate: int | None) -> str | None:
    if not bitrate:
        return None
    if bitrate >= 1_000_000:
        return f"{bitrate / 1_000_000:.1f} Mbps"
    if bitrate >= 1_000:
        return f"{bitrate / 1_000:.0f} kbps"
    return f"{bitrate} bps"


def _build_interface_chip_controls(statuses):
    if not statuses:
        return [
            ft.Text(
                "No interfaces detected",
                size=11,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
        ]

    chips = []
    for status in statuses:
        indicator_color = ft.Colors.GREEN if status["online"] else ft.Colors.ERROR
        tooltip = status["type"]
        bitrate_label = _format_bitrate(status.get("bitrate"))
        if bitrate_label:
            tooltip = f"{tooltip} • {bitrate_label}"

        chips.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CIRCLE, size=10, color=indicator_color),
                        ft.Text(status["name"], size=11),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#1C1F2B",
                border_radius=999,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
                tooltip=tooltip,
            ),
        )
    return chips


def _refresh_interface_status(summary_text, chip_wrap, updated_text):
    statuses = _get_interface_statuses()
    total = len(statuses)
    online = sum(1 for entry in statuses if entry["online"])

    if total == 0:
        summary_text.value = "No active interfaces"
        summary_text.color = ft.Colors.ERROR
    else:
        summary_text.value = f"{online}/{total} interfaces online"
        summary_text.color = ft.Colors.GREEN if online else ft.Colors.ERROR

    chip_wrap.controls = _build_interface_chip_controls(statuses)
    updated_text.value = f"Updated {datetime.now().strftime('%H:%M:%S')}"


def _build_status_section(page: ft.Page):
    summary_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    updated_text = ft.Text("", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    chip_wrap = ft.Row(
        spacing=6,
        run_spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    def refresh(_=None):
        _refresh_interface_status(summary_text, chip_wrap, updated_text)
        page.update()

    refresh()

    refresh_button = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Refresh status",
        on_click=refresh,
        icon_color=ft.Colors.BLUE_200,
    )

    section = ft.Column(
        spacing=12,
        controls=[
            ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LAN, size=18, color=ft.Colors.BLUE_200),
                            summary_text,
                        ],
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    refresh_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            chip_wrap,
            updated_text,
        ],
    )

    return section, refresh


def _build_storage_field(storage):
    storage_field = ft.TextField(
        label="Storage Information",
        value="",
        expand=True,
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=15,
        border_color=ft.Colors.GREY_700,
        text_style=ft.TextStyle(font_family="monospace", size=12),
    )

    def refresh():
        info = storage.get_storage_info()
        storage_field.value = "\n".join(f"{key}: {value}" for key, value in info.items())

    refresh()
    return storage_field, refresh


def open_settings_tab(page: ft.Page, tab_manager):
    """Open a settings tab with configuration, status, and storage info."""
    storage = get_storage_manager(page)
    config_path = _get_config_file_path()
    config_text = _read_config_text(config_path)
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

    def on_bgcolor_change(_):
        try:
            color_preview.bgcolor = page_bgcolor_field.value
            page.update()
        except Exception:
            pass

    page_bgcolor_field.on_change = on_bgcolor_change

    def show_snack(message, *, success=True):
        snack = ft.SnackBar(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.CHECK_CIRCLE if success else ft.Icons.ERROR,
                        color=ft.Colors.GREEN_400 if success else ft.Colors.RED_400,
                        size=20,
                    ),
                    ft.Text(message, color=ft.Colors.WHITE),
                ],
                tight=True,
            ),
            bgcolor=ft.Colors.GREEN_900 if success else ft.Colors.RED_900,
            duration=3000 if success else 4000,
        )
        page.overlay.append(snack)
        snack.open = True
        page.update()

    def on_save_config(_):
        try:
            _write_config_text(config_path, config_field.value)
            show_snack(f"Configuration saved to {config_path}")
        except Exception as exc:  # noqa: BLE001
            show_snack(f"Failed to save configuration: {exc}", success=False)

    def on_save_and_reload_config(_):
        try:
            _write_config_text(config_path, config_field.value)
        except Exception as exc:  # noqa: BLE001
            show_snack(f"Failed to save configuration: {exc}", success=False)
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

        async def do_reload():
            import ren_browser.app as app_module

            try:
                await app_module.reload_reticulum(page, on_reload_complete)
            except Exception as exc:  # noqa: BLE001
                loading_snack.open = False
                page.update()
                show_snack(f"Reload failed: {exc}", success=False)

        def on_reload_complete(success, error):
            loading_snack.open = False
            page.update()
            if success:
                show_snack("Reticulum reloaded successfully!")
            else:
                show_snack(f"Reload failed: {error}", success=False)

        page.run_task(do_reload)

    def on_save_app_settings(_):
        try:
            new_settings = {
                "horizontal_scroll": horizontal_scroll_switch.value,
                "page_bgcolor": page_bgcolor_field.value,
            }
            success = storage.save_app_settings(new_settings)
            if success:
                if hasattr(tab_manager, "apply_settings"):
                    tab_manager.apply_settings(new_settings)
                show_snack("Appearance settings saved and applied!")
            else:
                show_snack("Failed to save appearance settings", success=False)
        except Exception as exc:  # noqa: BLE001
            show_snack(f"Error saving appearance: {exc}", success=False)

    save_btn = ft.ElevatedButton(
        "Save Configuration",
        icon=ft.Icons.SAVE,
        on_click=on_save_config,
        style=_blue_button_style(),
    )
    save_reload_btn = ft.ElevatedButton(
        "Save & Hot Reload",
        icon=ft.Icons.REFRESH,
        on_click=on_save_and_reload_config,
        style=_blue_button_style(),
    )
    save_appearance_btn = ft.ElevatedButton(
        "Save Appearance",
        icon=ft.Icons.PALETTE,
        on_click=on_save_app_settings,
        style=_blue_button_style(),
    )

    status_content, refresh_status_section = _build_status_section(page)
    storage_field, refresh_storage_info = _build_storage_field(storage)

    appearance_content = ft.Column(
        spacing=16,
        controls=[
            ft.Text("Appearance Settings", size=18, weight=ft.FontWeight.BOLD),
            horizontal_scroll_switch,
            ft.Row(
                controls=[page_bgcolor_field, color_preview],
                alignment=ft.MainAxisAlignment.START,
                spacing=16,
            ),
            save_appearance_btn,
        ],
    )

    content_placeholder = ft.Container(expand=True, content=config_field)

    def show_config(_):
        content_placeholder.content = config_field
        page.update()

    def show_appearance(_):
        content_placeholder.content = appearance_content
        page.update()

    def show_status(_):
        content_placeholder.content = status_content
        refresh_status_section()

    def show_storage_info(_):
        refresh_storage_info()
        content_placeholder.content = storage_field
        page.update()

    def refresh_current_view(_):
        if content_placeholder.content == status_content:
            refresh_status_section()
        elif content_placeholder.content == storage_field:
            refresh_storage_info()
            page.update()

    btn_config = ft.FilledButton(
        "Configuration",
        icon=ft.Icons.SETTINGS,
        on_click=show_config,
        style=_blue_button_style(),
    )
    btn_appearance = ft.FilledButton(
        "Appearance",
        icon=ft.Icons.PALETTE,
        on_click=show_appearance,
        style=_blue_button_style(),
    )
    btn_status = ft.FilledButton(
        "Status",
        icon=ft.Icons.LAN,
        on_click=show_status,
        style=_blue_button_style(),
    )
    btn_storage = ft.FilledButton(
        "Storage",
        icon=ft.Icons.STORAGE,
        on_click=show_storage_info,
        style=_blue_button_style(),
    )
    btn_refresh = ft.IconButton(
        icon=ft.Icons.REFRESH,
        tooltip="Refresh",
        on_click=refresh_current_view,
        icon_color=ft.Colors.BLUE_400,
    )

    nav_card = ft.Container(
        content=ft.Row(
            controls=[btn_config, btn_appearance, btn_status, btn_storage, btn_refresh],
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

