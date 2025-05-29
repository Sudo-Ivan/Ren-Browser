from types import SimpleNamespace

import flet as ft

from ren_browser.renderer.micron.micron import render_micron
from ren_browser.renderer.plaintext.plaintext import render_plaintext


class TabsManager:
    def __init__(self, page: ft.Page):
        import ren_browser.app as app_module
        self.page = page
        # State: list of tabs and current index
        self.manager = SimpleNamespace(tabs=[], index=0)
        # UI components
        self.tab_bar = ft.Row(spacing=4)
        self.content_container = ft.Container(expand=True)

        # Initialize with default "Home" tab only, using selected renderer
        default_content = render_micron("Welcome to Ren Browser") if app_module.RENDERER == "micron" else render_plaintext("Welcome to Ren Browser")
        self._add_tab_internal("Home", default_content)
        # Action buttons
        self.add_btn = ft.IconButton(ft.Icons.ADD, tooltip="New Tab", on_click=self._on_add_click)
        self.close_btn = ft.IconButton(ft.Icons.CLOSE, tooltip="Close Tab", on_click=self._on_close_click)
        # Append add and close buttons
        self.tab_bar.controls.extend([self.add_btn, self.close_btn])
        # Select the first tab
        self.select_tab(0)

    def _add_tab_internal(self, title: str, content: ft.Control):
        idx = len(self.manager.tabs)
        # Create per-tab URL bar and GO button
        url_field = ft.TextField(label="URL", value=title, expand=True)
        go_btn = ft.IconButton(ft.Icons.OPEN_IN_BROWSER, tooltip="Load URL", on_click=lambda e, i=idx: self._on_tab_go(e, i))
        # Wrap the content in a Column: URL bar + initial content
        content_control = content
        tab_content = ft.Column(
            expand=True,
            controls=[
                ft.Row([url_field, go_btn]),
                content_control,
            ],
        )
        # Store tab data
        self.manager.tabs.append({
            "title": title,
            "url_field": url_field,
            "content_control": content_control,
            "content": tab_content,
        })
        # Create stylable tab button container
        btn = ft.Container(
            content=ft.Text(title),
            on_click=lambda e, i=idx: self.select_tab(i),
            padding=ft.padding.symmetric(horizontal=12, vertical=6),
            border_radius=5,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )
        # Insert before the add and close buttons
        insert_pos = max(0, len(self.tab_bar.controls) - 2)
        self.tab_bar.controls.insert(insert_pos, btn)

    def _on_add_click(self, e):
        title = f"Tab {len(self.manager.tabs) + 1}"
        # Render new tab content based on selected renderer
        content_text = f"Content for {title}"
        import ren_browser.app as app_module
        content = render_micron(content_text) if app_module.RENDERER == "micron" else render_plaintext(content_text)
        self._add_tab_internal(title, content)
        # Select the new tab
        self.select_tab(len(self.manager.tabs) - 1)
        self.page.update()

    def _on_close_click(self, e):
        # Do not allow closing all tabs
        if len(self.manager.tabs) <= 1:
            return
        idx = self.manager.index
        # Remove tab data and button
        self.manager.tabs.pop(idx)
        self.tab_bar.controls.pop(idx)
        # Reassign on_click handlers to correct indices
        for i, control in enumerate(self.tab_bar.controls[:-2]):
            control.on_click = lambda e, i=i: self.select_tab(i)
        # Adjust selected index
        new_idx = min(idx, len(self.manager.tabs) - 1)
        self.select_tab(new_idx)
        self.page.update()

    def select_tab(self, idx: int):
        self.manager.index = idx
        # Highlight active tab and dim others
        for i, control in enumerate(self.tab_bar.controls[:-2]):
            if i == idx:
                control.bgcolor = ft.Colors.PRIMARY_CONTAINER
            else:
                control.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        # Update displayed content
        self.content_container.content = self.manager.tabs[idx]["content"]
        self.page.update()

    def _on_tab_go(self, e, idx: int):
        """Handle loading a new URL in a specific tab (placeholder logic)."""
        tab = self.manager.tabs[idx]
        url = tab["url_field"].value.strip()
        if not url:
            return
        # Placeholder: update the content_control using selected renderer
        placeholder_text = f"Loading content for {url}"
        import ren_browser.app as app_module
        new_control = render_micron(placeholder_text) if app_module.RENDERER == "micron" else render_plaintext(placeholder_text)
        tab["content_control"] = new_control
        tab["content"].controls[1] = new_control
        # Refresh the displayed content if this tab is active
        if self.manager.index == idx:
            self.content_container.content = tab["content"]
        self.page.update()
