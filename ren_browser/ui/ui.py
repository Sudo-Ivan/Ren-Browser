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
    page.appbar = ft.AppBar()
    page.window.maximized = True

    page_fetcher = PageFetcher()
    announce_list = ft.ListView(expand=True, spacing=1)
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
                    if req.page_path.endswith(".mu"):
                        new_control = render_micron(result)
                    else:
                        new_control = render_plaintext(result)
                    tab["content_control"] = new_control
                    tab["content"].controls[0] = new_control
                    if tab_manager.manager.index == idx:
                        tab_manager.content_container.content = tab["content"]
                    page.update()
                page.run_thread(fetch_and_update)
            announce_list.controls.append(ft.TextButton(label, on_click=on_click_ann))
        page.update()
    AnnounceService(update_callback=update_announces)
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Text("Announcements", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, expand=True),
            ft.Divider(),
            announce_list,
        ],
    )
    page.appbar.leading = ft.IconButton(
        ft.Icons.MENU,
        tooltip="Toggle sidebar",
        on_click=lambda e: (setattr(page.drawer, "open", not page.drawer.open), page.update()),
    )

    tab_manager = TabsManager(page)
    from ren_browser.ui.settings import open_settings_tab
    page.appbar.actions = [ft.IconButton(ft.Icons.SETTINGS, tooltip="Settings", on_click=lambda e: open_settings_tab(page, tab_manager))]
    Shortcuts(page, tab_manager)
    url_bar = ft.Row(
        controls=[
            tab_manager.manager.tabs[tab_manager.manager.index]["url_field"],
            tab_manager.manager.tabs[tab_manager.manager.index]["go_btn"],
        ],
    )
    page.appbar.title = url_bar
    orig_select_tab = tab_manager.select_tab
    def _select_tab_and_update_url(i):
        orig_select_tab(i)
        tab = tab_manager.manager.tabs[i]
        url_bar.controls.clear()
        url_bar.controls.extend([tab["url_field"], tab["go_btn"]])
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
