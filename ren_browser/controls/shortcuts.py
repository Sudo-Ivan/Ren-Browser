import flet as ft


class Shortcuts:
    def __init__(self, page: ft.Page, tab_manager):
        """Attach keyboard event handler to page and delegate actions to tab_manager and UI."""
        self.page = page
        self.tab_manager = tab_manager
        page.on_keyboard_event = self.on_keyboard

    def on_keyboard(self, e: ft.KeyboardEvent):
        # Support Ctrl (and Meta on macOS)
        ctrl = e.ctrl or e.meta
        if not ctrl:
            return
        key = e.key
        # New tab: Ctrl+T
        if key.lower() == "t":
            self.tab_manager._on_add_click(None)
        # Close tab: Ctrl+W
        elif key.lower() == "w":
            self.tab_manager._on_close_click(None)
        # Focus URL bar: Ctrl+L
        elif key.lower() == "l":
            idx = self.tab_manager.manager.index
            field = self.tab_manager.manager.tabs[idx]["url_field"]
            field.focus()
        # Show announces drawer: Ctrl+A
        elif key.lower() == "a":
            self.page.drawer.open = True
        # Cycle through tabs: Ctrl+Tab / Ctrl+Shift+Tab
        elif key == "Tab":
            idx = self.tab_manager.manager.index
            count = len(self.tab_manager.manager.tabs)
            new_idx = (idx - 1) % count if e.shift else (idx + 1) % count
            self.tab_manager.select_tab(new_idx)
        else:
            return
        # Apply UI updates
        self.page.update()
