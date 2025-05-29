import flet as ft
from flet import Page

from ren_browser.announces.announces import AnnounceService
from ren_browser.controls.shortcuts import Shortcuts
from ren_browser.pages.page_request import PageFetcher, PageRequest
from ren_browser.renderer.micron.micron import render_micron
from ren_browser.renderer.plaintext.plaintext import render_plaintext
from ren_browser.tabs.tabs import TabsManager


def build_ui(page: Page):
    import ren_browser.app as app_module
    # Page properties
    page.title = "Ren Browser"
    page.theme_mode = ft.ThemeMode.DARK
    page.appbar = ft.AppBar(title=ft.Text("Ren Browser"))
    page.padding = 20
    # Maximize window for wide screens
    page.window.maximized = True

    # Initialize page fetcher and announce service
    page_fetcher = PageFetcher()
    # Sidebar announces list in a scrollable ListView within a NavigationDrawer
    announce_list = ft.ListView(expand=True, spacing=1)
    def update_announces(ann_list):
        announce_list.controls.clear()
        for ann in ann_list:
            label = ann.display_name or ann.destination_hash
            # Use display_name for tab title, fallback to "Anonymous"; set URL bar to full path
            def on_click_ann(e, dest=ann.destination_hash, disp=ann.display_name):
                title = disp or "Anonymous"
                # Full URL including page path
                full_url = f"{dest}:/page/index.mu"
                placeholder = render_plaintext(f"Fetching content for {full_url}")
                tab_manager._add_tab_internal(title, placeholder)
                idx = len(tab_manager.manager.tabs) - 1
                # Set URL bar to full URL
                tab = tab_manager.manager.tabs[idx]
                tab["url_field"].value = full_url
                # Select the new tab and refresh UI
                tab_manager.select_tab(idx)
                page.update()
                def fetch_and_update():
                    req = PageRequest(destination_hash=dest, page_path="/page/index.mu")
                    try:
                        result = page_fetcher.fetch_page(req)
                    except Exception as ex:
                        result = f"Error: {ex}"
                    # Skip update if tab has been closed or index out of range
                    try:
                        tab = tab_manager.manager.tabs[idx]
                    except IndexError:
                        return
                    # Use micron renderer for .mu pages, fallback to plaintext
                    if req.page_path.endswith(".mu"):
                        new_control = render_micron(result)
                    else:
                        new_control = render_plaintext(result)
                    tab["content_control"] = new_control
                    # Replace the content control in the tab's column
                    tab["content"].controls[0] = new_control
                    if tab_manager.manager.index == idx:
                        tab_manager.content_container.content = tab["content"]
                    page.update()
                page.run_thread(fetch_and_update)
            announce_list.controls.append(ft.TextButton(label, on_click=on_click_ann))
        page.update()
    AnnounceService(update_callback=update_announces)
    # Make sidebar collapsible via drawer
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.Text("Announcements", weight=ft.FontWeight.BOLD),
            ft.Divider(),
            announce_list,
        ],
    )
    # Add hamburger button to toggle drawer
    page.appbar.leading = ft.IconButton(
        ft.Icons.MENU,
        tooltip="Toggle sidebar",
        on_click=lambda e: (setattr(page.drawer, 'open', not page.drawer.open), page.update()),
    )

    # Dynamic tabs manager for pages
    tab_manager = TabsManager(page)
    Shortcuts(page, tab_manager)
    url_bar = ft.Row(
        controls=[
            tab_manager.manager.tabs[tab_manager.manager.index]["url_field"],
            tab_manager.manager.tabs[tab_manager.manager.index]["go_btn"],
        ],
    )
    orig_select_tab = tab_manager.select_tab
    def _select_tab_and_update_url(i):
        orig_select_tab(i)
        tab = tab_manager.manager.tabs[i]
        url_bar.controls.clear()
        url_bar.controls.extend([tab["url_field"], tab["go_btn"]])
        page.update()
    tab_manager.select_tab = _select_tab_and_update_url
    def _update_content_width(e=None):
        # Use page.width for current content width
        width = page.width - (page.padding * 2)
        if width < 0:
            width = 0
        tab_manager.content_container.width = width
    _update_content_width()
    page.on_resized = lambda e: (_update_content_width(), page.update())
    main_area = ft.Column(
        expand=True,
        controls=[
            tab_manager.tab_bar,
            url_bar,
            tab_manager.content_container,
        ],
    )

    # Layout: main content only (sidebar in drawer)
    layout = ft.Row(expand=True, controls=[main_area])

    # Render main layout with status
    page.add(
        ft.Column(
            expand=True,
            controls=[
                layout,
                ft.Row(
                    [
                        ft.Text(
                            f"Renderer: {app_module.RENDERER}",
                            color=ft.Colors.GREY,
                            size=12,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
        ),
    )
