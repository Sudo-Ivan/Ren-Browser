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

    def __init__(self, page: ft.Page):
        """Initialize the tab manager.

        Args:
            page: Flet page instance for UI updates.

        """
        import ren_browser.app as app_module
        self.page = page
        self.manager = SimpleNamespace(tabs=[], index=0)
        self.tab_bar = ft.Row(spacing=4)
        self.content_container = ft.Container(expand=True, bgcolor=ft.Colors.BLACK, padding=ft.padding.all(5))

        default_content = render_micron("Welcome to Ren Browser") if app_module.RENDERER == "micron" else render_plaintext("Welcome to Ren Browser")
        self._add_tab_internal("Home", default_content)
        self.add_btn = ft.IconButton(ft.Icons.ADD, tooltip="New Tab", on_click=self._on_add_click)
        self.close_btn = ft.IconButton(ft.Icons.CLOSE, tooltip="Close Tab", on_click=self._on_close_click)
        self.tab_bar.controls.extend([self.add_btn, self.close_btn])
        self.select_tab(0)

    def _add_tab_internal(self, title: str, content: ft.Control):
        idx = len(self.manager.tabs)
        url_field = ft.TextField(
            value=title,
            expand=True,
            text_style=ft.TextStyle(size=12),
            content_padding=ft.padding.only(top=8, bottom=8, left=8, right=8)
        )
        go_btn = ft.IconButton(ft.Icons.OPEN_IN_BROWSER, tooltip="Load URL", on_click=lambda e, i=idx: self._on_tab_go(e, i))
        content_control = content
        tab_content = ft.Column(
            expand=True,
            controls=[
                content_control,
            ],
        )
        self.manager.tabs.append({
            "title": title,
            "url_field": url_field,
            "go_btn": go_btn,
            "content_control": content_control,
            "content": tab_content,
        })
        btn = ft.Container(
            content=ft.Text(title),
            on_click=lambda e, i=idx: self.select_tab(i),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=5,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        insert_pos = max(0, len(self.tab_bar.controls) - 2)
        self.tab_bar.controls.insert(insert_pos, btn)

    def _on_add_click(self, e):
        title = f"Tab {len(self.manager.tabs) + 1}"
        content_text = f"Content for {title}"
        import ren_browser.app as app_module
        content = render_micron(content_text) if app_module.RENDERER == "micron" else render_plaintext(content_text)
        self._add_tab_internal(title, content)
        self.select_tab(len(self.manager.tabs) - 1)
        self.page.update()

    def _on_close_click(self, e):
        if len(self.manager.tabs) <= 1:
            return
        idx = self.manager.index
        self.manager.tabs.pop(idx)
        self.tab_bar.controls.pop(idx)
        for i, control in enumerate(self.tab_bar.controls[:-2]):
            control.on_click = lambda e, i=i: self.select_tab(i)
        new_idx = min(idx, len(self.manager.tabs) - 1)
        self.select_tab(new_idx)
        self.page.update()

    def select_tab(self, idx: int):
        """Select and display the tab at the given index.

        Args:
            idx: Index of the tab to select.

        """
        self.manager.index = idx
        for i, control in enumerate(self.tab_bar.controls[:-2]):
            if i == idx:
                control.bgcolor = ft.Colors.PRIMARY_CONTAINER
            else:
                control.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.content_container.content = self.manager.tabs[idx]["content"]
        self.page.update()

    def _on_tab_go(self, e, idx: int):
        tab = self.manager.tabs[idx]
        url = tab["url_field"].value.strip()
        if not url:
            return
        placeholder_text = f"Loading content for {url}"
        import ren_browser.app as app_module
        new_control = render_micron(placeholder_text) if app_module.RENDERER == "micron" else render_plaintext(placeholder_text)
        tab["content_control"] = new_control
        tab["content"].controls[0] = new_control
        if self.manager.index == idx:
            self.content_container.content = tab["content"]
        self.page.update()
