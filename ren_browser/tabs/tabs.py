"""Tab management system for Ren Browser.

Provides tab creation, switching, and content management functionality
for the browser interface.
"""

from types import SimpleNamespace

import flet as ft

from ren_browser.renderer.micron import render_micron
from ren_browser.renderer.plaintext import render_plaintext


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
        self.tab_bar = ft.Row(
            spacing=4,
        )
        self.overflow_menu = None
        self.content_container = ft.Container(
            expand=True, bgcolor=ft.Colors.BLACK, padding=ft.padding.all(5),
        )

        default_content = (
            render_micron("Welcome to Ren Browser")
            if app_module.RENDERER == "micron"
            else render_plaintext("Welcome to Ren Browser")
        )
        self._add_tab_internal("Home", default_content)
        self.add_btn = ft.IconButton(
            ft.Icons.ADD, tooltip="New Tab", on_click=self._on_add_click,
        )
        self.close_btn = ft.IconButton(
            ft.Icons.CLOSE, tooltip="Close Tab", on_click=self._on_close_click,
        )
        self.tab_bar.controls.append(self.add_btn)
        self.tab_bar.controls.append(self.close_btn)
        self.select_tab(0)
        self._update_tab_visibility()

    def _on_resize(self, e) -> None:  # type: ignore
        """Handle page resize event and update tab visibility."""
        self._update_tab_visibility()

    def _update_tab_visibility(self) -> None:
        """Dynamically adjust tab visibility based on page width.

        Hides tabs that do not fit and moves them to an overflow menu.
        """
        if not self.page.width or self.page.width == 0:
            return

        if self.overflow_menu and self.overflow_menu in self.tab_bar.controls:
            self.tab_bar.controls.remove(self.overflow_menu)
            self.overflow_menu = None

        """Estimate available width for tabs (Page width - buttons - padding)."""
        available_width = self.page.width - 100

        cumulative_width = 0
        visible_tabs_count = 0

        tab_containers = [c for c in self.tab_bar.controls if isinstance(c, ft.Container)]

        for i, tab in enumerate(self.manager.tabs):
            """Estimate tab width: (char count * avg char width) + padding + spacing."""
            estimated_width = len(tab["title"]) * 10 + 32 + self.tab_bar.spacing

            """Always show at least one tab."""
            if cumulative_width + estimated_width <= available_width or i == 0:
                cumulative_width += estimated_width
                if i < len(tab_containers):
                    tab_containers[i].visible = True
                visible_tabs_count += 1
            elif i < len(tab_containers):
                tab_containers[i].visible = False

        if len(self.manager.tabs) > visible_tabs_count:
            """Move extra tabs to overflow menu."""
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

            self.tab_bar.controls.insert(visible_tabs_count, self.overflow_menu)

    def _add_tab_internal(self, title: str, content: ft.Control) -> None:
        """Add a new tab to the manager with the given title and content."""
        idx = len(self.manager.tabs)
        url_field = ft.TextField(
            value=title,
            expand=True,
            text_style=ft.TextStyle(size=12),
            content_padding=ft.padding.only(top=8, bottom=8, left=8, right=8),
        )
        go_btn = ft.IconButton(
            ft.Icons.OPEN_IN_BROWSER,
            tooltip="Load URL",
            on_click=lambda e, i=idx: self._on_tab_go(e, i),
        )
        content_control = content
        tab_content = ft.Column(
            expand=True,
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
            content=ft.Text(title),
            on_click=lambda e, i=idx: self.select_tab(i),  # type: ignore
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=5,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        """Insert the new tab before the add/close buttons."""
        insert_pos = max(0, len(self.tab_bar.controls) - 2)
        self.tab_bar.controls.insert(insert_pos, tab_container)
        self._update_tab_visibility()

    def _on_add_click(self, e) -> None:  # type: ignore
        """Handle the add tab button click event."""
        title = f"Tab {len(self.manager.tabs) + 1}"
        content_text = f"Content for {title}"
        import ren_browser.app as app_module

        content = (
            render_micron(content_text)
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

        tab_containers = [c for c in self.tab_bar.controls if isinstance(c, ft.Container)]
        control_to_remove = tab_containers[idx]

        self.manager.tabs.pop(idx)
        self.tab_bar.controls.remove(control_to_remove)

        updated_tab_containers = [c for c in self.tab_bar.controls if isinstance(c, ft.Container)]
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

        tab_containers = [c for c in self.tab_bar.controls if isinstance(c, ft.Container)]
        for i, control in enumerate(tab_containers):
            if i == idx:
                control.bgcolor = ft.Colors.PRIMARY_CONTAINER
            else:
                control.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST

        self.content_container.content = self.manager.tabs[idx]["content"]
        self.page.update()

    def _on_tab_go(self, e, idx: int) -> None:  # type: ignore
        """Handle the go button click event for a tab, loading new content."""
        tab = self.manager.tabs[idx]
        url = tab["url_field"].value.strip()
        if not url:
            return
        placeholder_text = f"Loading content for {url}"
        import ren_browser.app as app_module

        new_control = (
            render_micron(placeholder_text)
            if app_module.RENDERER == "micron"
            else render_plaintext(placeholder_text)
        )
        tab["content_control"] = new_control
        tab["content"].controls[0] = new_control
        if self.manager.index == idx:
            self.content_container.content = tab["content"]
        self.page.update()
