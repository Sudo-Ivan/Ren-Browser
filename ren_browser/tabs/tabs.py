"""Tab management system for Ren Browser.

Provides tab creation, switching, and content management functionality
for the browser interface.
"""

from types import SimpleNamespace

import flet as ft

from ren_browser.pages.page_request import PageFetcher, PageRequest
from ren_browser.renderer.micron import render_micron
from ren_browser.renderer.plaintext import render_plaintext
from ren_browser.storage.storage import get_storage_manager


class TabsManager:
    """Manages browser tabs and their content.

    Handles tab creation, switching, closing, and content rendering.
    """

    def __init__(self, page: ft.Page) -> None:
        """Initialize the tab manager.

        Args:
            page: Flet page instance for UI updates.

        """
        import ren_browser.app as app_module

        self.page = page
        self.page.on_resize = self._on_resize
        self.manager = SimpleNamespace(tabs=[], index=0)
        
        storage = get_storage_manager(page)
        self.settings = storage.load_app_settings()
        
        self.tab_bar = ft.Container(
            content=ft.Row(
                spacing=6,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.padding.symmetric(horizontal=8, vertical=8),
        )
        self.overflow_menu = None
        self.content_container = ft.Container(
            expand=True,
            bgcolor=self.settings.get("page_bgcolor", ft.Colors.BLACK),
            padding=ft.padding.all(16),
        )

        def handle_link_click_home(link_url):
            if len(self.manager.tabs) > 0:
                tab = self.manager.tabs[0]
                full_url = link_url
                if ":" not in link_url:
                    full_url = f"{link_url}:/page/index.mu"
                tab["url_field"].value = full_url
                self._on_tab_go(None, 0)

        default_content = (
            render_micron("Welcome to Ren Browser", on_link_click=handle_link_click_home)
            if app_module.RENDERER == "micron"
            else render_plaintext("Welcome to Ren Browser")
        )
        self._add_tab_internal("Home", default_content)
        self.add_btn = ft.IconButton(
            ft.Icons.ADD,
            tooltip="New Tab",
            on_click=self._on_add_click,
            icon_color=ft.Colors.WHITE,
        )
        self.close_btn = ft.IconButton(
            ft.Icons.CLOSE,
            tooltip="Close Tab",
            on_click=self._on_close_click,
            icon_color=ft.Colors.WHITE,
        )
        self.tab_bar.content.controls.append(self.add_btn)
        self.tab_bar.content.controls.append(self.close_btn)
        self.select_tab(0)
        self._update_tab_visibility()

    def _on_resize(self, e) -> None:  # type: ignore
        """Handle page resize event and update tab visibility."""
        self._update_tab_visibility()

    def apply_settings(self, settings: dict) -> None:
        """Apply appearance settings to the tab manager.

        Args:
            settings: Dictionary containing appearance settings.

        """
        self.settings = settings
        bgcolor = settings.get("page_bgcolor", "#000000")
        self.content_container.bgcolor = bgcolor
        
        horizontal_scroll = settings.get("horizontal_scroll", False)
        scroll_mode = ft.ScrollMode.ALWAYS if horizontal_scroll else ft.ScrollMode.AUTO
        
        for tab in self.manager.tabs:
            if "content" in tab and hasattr(tab["content"], "scroll"):
                tab["content"].scroll = scroll_mode
            if "content_control" in tab and hasattr(tab["content_control"], "scroll"):
                tab["content_control"].scroll = scroll_mode
        
        if self.content_container.content:
            self.content_container.content.update()
        self.page.update()

    def _update_tab_visibility(self) -> None:
        """Dynamically adjust tab visibility based on page width.

        Hides tabs that do not fit and moves them to an overflow menu.
        """
        if not self.page.width or self.page.width == 0:
            return

        if self.overflow_menu and self.overflow_menu in self.tab_bar.content.controls:
            self.tab_bar.content.controls.remove(self.overflow_menu)
            self.overflow_menu = None

        available_width = self.page.width - 100

        cumulative_width = 0
        visible_tabs_count = 0

        tab_containers = [c for c in self.tab_bar.content.controls if isinstance(c, ft.Container)]

        for i, tab in enumerate(self.manager.tabs):
            estimated_width = len(tab["title"]) * 10 + 32 + self.tab_bar.content.spacing

            if cumulative_width + estimated_width <= available_width or i == 0:
                cumulative_width += estimated_width
                if i < len(tab_containers):
                    tab_containers[i].visible = True
                visible_tabs_count += 1
            elif i < len(tab_containers):
                tab_containers[i].visible = False

        if len(self.manager.tabs) > visible_tabs_count:
            overflow_items = []
            for i in range(visible_tabs_count, len(self.manager.tabs)):
                tab_data = self.manager.tabs[i]
                overflow_items.append(
                    ft.PopupMenuItem(
                        text=tab_data["title"],
                        on_click=lambda e, idx=i: self.select_tab(idx),  # type: ignore
                    ),
                )

            self.overflow_menu = ft.PopupMenuButton(
                icon=ft.Icons.MORE_HORIZ,
                tooltip=f"{len(self.manager.tabs) - visible_tabs_count} more tabs",
                items=overflow_items,
            )

            self.tab_bar.content.controls.insert(visible_tabs_count, self.overflow_menu)

    def _add_tab_internal(self, title: str, content: ft.Control) -> None:
        """Add a new tab to the manager with the given title and content."""
        idx = len(self.manager.tabs)
        url_field = ft.TextField(
            value=title,
            expand=True,
            text_style=ft.TextStyle(size=14),
            content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=24,
            border_color=ft.Colors.GREY_700,
            focused_border_color=ft.Colors.BLUE_400,
            bgcolor=ft.Colors.GREY_800,
            prefix_icon=ft.Icons.SEARCH,
        )
        go_btn = ft.IconButton(
            ft.Icons.ARROW_FORWARD,
            tooltip="Go",
            on_click=lambda e, i=idx: self._on_tab_go(e, i),
            icon_color=ft.Colors.BLUE_400,
            bgcolor=ft.Colors.BLUE_900,
        )
        content_control = content
        horizontal_scroll = self.settings.get("horizontal_scroll", False)
        scroll_mode = ft.ScrollMode.ALWAYS if horizontal_scroll else ft.ScrollMode.AUTO
        
        tab_content = ft.Column(
            expand=True,
            scroll=scroll_mode,
            controls=[
                content_control,
            ],
        )
        self.manager.tabs.append(
            {
                "title": title,
                "url_field": url_field,
                "go_btn": go_btn,
                "content_control": content_control,
                "content": tab_content,
            },
        )
        tab_container = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        title,
                        size=13,
                        weight=ft.FontWeight.W_500,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=8,
            ),
            on_click=lambda e, i=idx: self.select_tab(i),  # type: ignore
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            border_radius=8,
            bgcolor=ft.Colors.GREY_800,
            ink=True,
            width=150,
        )
        insert_pos = max(0, len(self.tab_bar.content.controls) - 2)
        self.tab_bar.content.controls.insert(insert_pos, tab_container)
        self._update_tab_visibility()

    def _on_add_click(self, e) -> None:  # type: ignore
        """Handle the add tab button click event."""
        title = f"Tab {len(self.manager.tabs) + 1}"
        content_text = f"Content for {title}"
        import ren_browser.app as app_module

        new_idx = len(self.manager.tabs)

        def handle_link_click_new(link_url):
            tab = self.manager.tabs[new_idx]
            full_url = link_url
            if ":" not in link_url:
                full_url = f"{link_url}:/page/index.mu"
            tab["url_field"].value = full_url
            self._on_tab_go(None, new_idx)

        content = (
            render_micron(content_text, on_link_click=handle_link_click_new)
            if app_module.RENDERER == "micron"
            else render_plaintext(content_text)
        )
        self._add_tab_internal(title, content)
        self.select_tab(len(self.manager.tabs) - 1)
        self.page.update()

    def _on_close_click(self, e) -> None:  # type: ignore
        """Handle the close tab button click event."""
        if len(self.manager.tabs) <= 1:
            return
        idx = self.manager.index

        tab_containers = [c for c in self.tab_bar.content.controls if isinstance(c, ft.Container)]
        control_to_remove = tab_containers[idx]

        self.manager.tabs.pop(idx)
        self.tab_bar.content.controls.remove(control_to_remove)

        updated_tab_containers = [c for c in self.tab_bar.content.controls if isinstance(c, ft.Container)]
        for i, control in enumerate(updated_tab_containers):
            control.on_click = lambda e, i=i: self.select_tab(i)  # type: ignore

        new_idx = min(idx, len(self.manager.tabs) - 1)
        self.select_tab(new_idx)
        self._update_tab_visibility()
        self.page.update()

    def select_tab(self, idx: int) -> None:
        """Select and display the tab at the given index.

        Args:
            idx: Index of the tab to select.

        """
        self.manager.index = idx

        tab_containers = [c for c in self.tab_bar.content.controls if isinstance(c, ft.Container)]
        for i, control in enumerate(tab_containers):
            if i == idx:
                control.bgcolor = ft.Colors.BLUE_900
                control.border = ft.border.all(2, ft.Colors.BLUE_400)
            else:
                control.bgcolor = ft.Colors.GREY_800
                control.border = None

        self.content_container.content = self.manager.tabs[idx]["content"]
        self.page.update()

    def _on_tab_go(self, e, idx: int) -> None:  # type: ignore
        """Handle the go button click event for a tab, loading new content."""
        tab = self.manager.tabs[idx]
        url = tab["url_field"].value.strip()
        if not url:
            return
        
        placeholder_text = f"Loading content for {url}..."
        import ren_browser.app as app_module

        current_node_hash = None
        if ":" in url:
            current_node_hash = url.split(":")[0]

        def handle_link_click(link_url):
            full_url = link_url
            if ":" not in link_url:
                full_url = f"{link_url}:/page/index.mu"
            elif link_url.startswith(":/"):
                if current_node_hash:
                    full_url = f"{current_node_hash}{link_url}"
                else:
                    full_url = link_url
            tab["url_field"].value = full_url
            self._on_tab_go(None, idx)

        placeholder_control = (
            render_micron(placeholder_text, on_link_click=handle_link_click)
            if app_module.RENDERER == "micron"
            else render_plaintext(placeholder_text)
        )
        tab["content_control"] = placeholder_control
        tab["content"].controls[0] = placeholder_control
        if self.manager.index == idx:
            self.content_container.content = tab["content"]
        self.page.update()

        def fetch_and_update():
            parts = url.split(":", 1)
            if len(parts) != 2:
                result = f"Error: Invalid URL format. Expected format: hash:/page/path"
                page_path = ""
            else:
                dest_hash = parts[0]
                page_path = parts[1] if parts[1].startswith("/") else f"/{parts[1]}"
                
                req = PageRequest(destination_hash=dest_hash, page_path=page_path)
                page_fetcher = PageFetcher()
                try:
                    result = page_fetcher.fetch_page(req)
                except Exception as ex:
                    app_module.log_error(str(ex))
                    result = f"Error: {ex}"
            
            try:
                tab = self.manager.tabs[idx]
            except IndexError:
                return

            if page_path and page_path.endswith(".mu"):
                new_control = render_micron(result, on_link_click=handle_link_click)
            else:
                new_control = render_plaintext(result)
            
            tab["content_control"] = new_control
            tab["content"].controls[0] = new_control
            if self.manager.index == idx:
                self.content_container.content = tab["content"]
            self.page.update()

        self.page.run_thread(fetch_and_update)
