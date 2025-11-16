"""Main UI construction for Ren Browser.

Builds the complete browser interface including tabs, navigation,
announce handling, and content rendering.
"""

import flet as ft
from flet import Page

from ren_browser.announces.announces import AnnounceService
from ren_browser.controls.shortcuts import Shortcuts
from ren_browser.pages.page_request import PageFetcher, PageRequest
from ren_browser.renderer.micron import render_micron
from ren_browser.renderer.plaintext import render_plaintext
from ren_browser.tabs.tabs import TabsManager


def build_ui(page: Page):
    """Build and configure the main browser UI.

    Args:
        page: Flet page instance to build UI on.

    """
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_400,
            on_primary=ft.Colors.WHITE,
            surface=ft.Colors.BLACK,
            on_surface=ft.Colors.WHITE,
            background=ft.Colors.BLACK,
            on_background=ft.Colors.WHITE,
        ),
    )
    page.bgcolor = ft.Colors.BLACK
    page.appbar = ft.AppBar(
        bgcolor=ft.Colors.GREY_900,
        elevation=2,
    )
    page.window.maximized = True
    page.padding = 0

    page_fetcher = PageFetcher()
    announce_list = ft.ListView(expand=True, spacing=8, padding=ft.padding.all(8))

    def update_announces(ann_list):
        announce_list.controls.clear()
        for ann in ann_list:
            label = ann.display_name or ann.destination_hash

            def on_click_ann(e, dest=ann.destination_hash, disp=ann.display_name):
                title = disp or "Anonymous"
                full_url = f"{dest}:/page/index.mu"
                placeholder = render_plaintext(f"Fetching content for {full_url}")
                tab_manager._add_tab_internal(title, placeholder)
                idx = len(tab_manager.manager.tabs) - 1
                tab = tab_manager.manager.tabs[idx]
                tab["url_field"].value = full_url
                tab_manager.select_tab(idx)
                page.update()

                def fetch_and_update():
                    req = PageRequest(destination_hash=dest, page_path="/page/index.mu")
                    try:
                        result = page_fetcher.fetch_page(req)
                    except Exception as ex:
                        import ren_browser.app as app_module

                        app_module.log_error(str(ex))
                        result = f"Error: {ex}"
                    try:
                        tab = tab_manager.manager.tabs[idx]
                    except IndexError:
                        return

                    def handle_link_click(url):
                        full_url = url
                        if ":" not in url:
                            full_url = f"{url}:/page/index.mu"
                        elif url.startswith(":/"):
                            full_url = f"{dest}{url}"
                        tab["url_field"].value = full_url
                        tab_manager._on_tab_go(None, idx)

                    if req.page_path.endswith(".mu"):
                        new_control = render_micron(
                            result, on_link_click=handle_link_click
                        )
                    else:
                        new_control = render_plaintext(result)
                    tab["content_control"] = new_control
                    tab["content"].controls[0] = new_control
                    if tab_manager.manager.index == idx:
                        tab_manager.content_container.content = tab["content"]
                    page.update()

                page.run_thread(fetch_and_update)

            announce_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LANGUAGE, size=20, color=ft.Colors.BLUE_400),
                        ft.Text(
                            label,
                            size=14,
                            weight=ft.FontWeight.W_500,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=12,
                ),
                padding=ft.padding.all(12),
                border_radius=8,
                bgcolor=ft.Colors.GREY_800,
                ink=True,
                on_click=on_click_ann,
            )
            announce_list.controls.append(announce_card)
        page.update()

    AnnounceService(update_callback=update_announces)
    page.drawer = ft.NavigationDrawer(
        bgcolor=ft.Colors.GREY_900,
        elevation=8,
        controls=[
            ft.Container(
                content=ft.Text(
                    "Announcements",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=20),
            ),
            ft.Divider(height=1, color=ft.Colors.GREY_700),
            announce_list,
        ],
    )
    page.appbar.leading = ft.IconButton(
        ft.Icons.MENU,
        tooltip="Announcements",
        icon_color=ft.Colors.WHITE,
        on_click=lambda e: (
            setattr(page.drawer, "open", not page.drawer.open),
            page.update(),
        ),
    )

    tab_manager = TabsManager(page)
    from ren_browser.ui.settings import open_settings_tab

    page.appbar.actions = [
        ft.IconButton(
            ft.Icons.SETTINGS,
            tooltip="Settings",
            icon_color=ft.Colors.WHITE,
            on_click=lambda e: open_settings_tab(page, tab_manager),
        ),
    ]
    Shortcuts(page, tab_manager)
    url_bar = ft.Container(
        content=ft.Row(
            controls=[
                tab_manager.manager.tabs[tab_manager.manager.index]["url_field"],
                tab_manager.manager.tabs[tab_manager.manager.index]["go_btn"],
            ],
            spacing=8,
        ),
        expand=True,
        padding=ft.padding.symmetric(horizontal=8),
    )
    page.appbar.title = url_bar
    orig_select_tab = tab_manager.select_tab

    def _select_tab_and_update_url(i):
        orig_select_tab(i)
        tab = tab_manager.manager.tabs[i]
        url_bar.content.controls.clear()
        url_bar.content.controls.extend([tab["url_field"], tab["go_btn"]])
        page.update()

    tab_manager.select_tab = _select_tab_and_update_url

    def _update_content_width(e=None):
        tab_manager.content_container.width = page.width

    _update_content_width()
    page.on_resized = lambda e: (_update_content_width(), page.update())
    main_area = ft.Column(
        expand=True,
        controls=[tab_manager.tab_bar, tab_manager.content_container],
    )

    layout = ft.Row(expand=True, controls=[main_area])

    page.add(
        ft.Column(
            expand=True,
            controls=[
                layout,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        ),
    )
