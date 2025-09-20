from unittest.mock import Mock

import pytest

from ren_browser.controls.shortcuts import Shortcuts


class TestShortcuts:
    """Test cases for the Shortcuts class."""

    @pytest.fixture
    def mock_tab_manager(self):
        """Create a mock tab manager for testing."""
        manager = Mock()
        manager.manager.index = 0
        manager.manager.tabs = [{"url_field": Mock()}]
        manager._on_add_click = Mock()
        manager._on_close_click = Mock()
        manager.select_tab = Mock()
        return manager

    @pytest.fixture
    def shortcuts(self, mock_page, mock_tab_manager):
        """Create a Shortcuts instance for testing."""
        return Shortcuts(mock_page, mock_tab_manager)

    def test_shortcuts_init(self, mock_page, mock_tab_manager):
        """Test Shortcuts initialization."""
        shortcuts = Shortcuts(mock_page, mock_tab_manager)

        assert shortcuts.page == mock_page
        assert shortcuts.tab_manager == mock_tab_manager
        assert mock_page.on_keyboard_event == shortcuts.on_keyboard

    def test_new_tab_shortcut_ctrl_t(self, shortcuts, mock_tab_manager):
        """Test Ctrl+T shortcut for new tab."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "t"
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_add_click.assert_called_once_with(None)
        shortcuts.page.update.assert_called_once()

    def test_new_tab_shortcut_meta_t(self, shortcuts, mock_tab_manager):
        """Test Meta+T shortcut for new tab (macOS)."""
        event = Mock()
        event.ctrl = False
        event.meta = True
        event.key = "T"
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_add_click.assert_called_once_with(None)

    def test_close_tab_shortcut_ctrl_w(self, shortcuts, mock_tab_manager):
        """Test Ctrl+W shortcut for close tab."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "w"
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_close_click.assert_called_once_with(None)
        shortcuts.page.update.assert_called_once()

    def test_focus_url_bar_shortcut_ctrl_l(self, shortcuts, mock_tab_manager):
        """Test Ctrl+L shortcut for focusing URL bar."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "l"
        event.shift = False

        url_field = Mock()
        mock_tab_manager.manager.tabs = [{"url_field": url_field}]
        mock_tab_manager.manager.index = 0

        shortcuts.on_keyboard(event)

        url_field.focus.assert_called_once()
        shortcuts.page.update.assert_called_once()

    def test_show_announces_drawer_ctrl_a(self, shortcuts):
        """Test Ctrl+A shortcut for showing announces drawer."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "a"
        event.shift = False

        shortcuts.page.drawer = Mock()
        shortcuts.page.drawer.open = False

        shortcuts.on_keyboard(event)

        assert shortcuts.page.drawer.open is True
        shortcuts.page.update.assert_called_once()

    def test_cycle_tabs_forward_ctrl_tab(self, shortcuts, mock_tab_manager):
        """Test Ctrl+Tab for cycling tabs forward."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "Tab"
        event.shift = False

        mock_tab_manager.manager.index = 0
        mock_tab_manager.manager.tabs = [Mock(), Mock(), Mock()]  # 3 tabs

        shortcuts.on_keyboard(event)

        mock_tab_manager.select_tab.assert_called_once_with(1)
        shortcuts.page.update.assert_called_once()

    def test_cycle_tabs_backward_ctrl_shift_tab(self, shortcuts, mock_tab_manager):
        """Test Ctrl+Shift+Tab for cycling tabs backward."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "Tab"
        event.shift = True

        mock_tab_manager.manager.index = 1
        mock_tab_manager.manager.tabs = [Mock(), Mock(), Mock()]  # 3 tabs

        shortcuts.on_keyboard(event)

        mock_tab_manager.select_tab.assert_called_once_with(0)
        shortcuts.page.update.assert_called_once()

    def test_cycle_tabs_wrap_around_forward(self, shortcuts, mock_tab_manager):
        """Test tab cycling wraps around when going forward from last tab."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "Tab"
        event.shift = False

        mock_tab_manager.manager.index = 2  # Last tab
        mock_tab_manager.manager.tabs = [Mock(), Mock(), Mock()]  # 3 tabs

        shortcuts.on_keyboard(event)

        mock_tab_manager.select_tab.assert_called_once_with(0)  # Wrap to first

    def test_cycle_tabs_wrap_around_backward(self, shortcuts, mock_tab_manager):
        """Test tab cycling wraps around when going backward from first tab."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "Tab"
        event.shift = True

        mock_tab_manager.manager.index = 0  # First tab
        mock_tab_manager.manager.tabs = [Mock(), Mock(), Mock()]  # 3 tabs

        shortcuts.on_keyboard(event)

        mock_tab_manager.select_tab.assert_called_once_with(2)  # Wrap to last

    def test_no_ctrl_or_meta_key_returns_early(self, shortcuts, mock_tab_manager):
        """Test that shortcuts without Ctrl or Meta key don't trigger actions."""
        event = Mock()
        event.ctrl = False
        event.meta = False
        event.key = "t"
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_add_click.assert_not_called()
        shortcuts.page.update.assert_not_called()

    def test_unknown_key_returns_early(self, shortcuts, mock_tab_manager):
        """Test that unknown key combinations don't trigger actions."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "z"  # Unknown shortcut
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_add_click.assert_not_called()
        shortcuts.page.update.assert_not_called()

    def test_case_insensitive_keys(self, shortcuts, mock_tab_manager):
        """Test that shortcuts work with uppercase keys."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "T"  # Uppercase
        event.shift = False

        shortcuts.on_keyboard(event)

        mock_tab_manager._on_add_click.assert_called_once_with(None)

    def test_multiple_tabs_url_field_access(self, shortcuts, mock_tab_manager):
        """Test URL field access with multiple tabs."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "l"
        event.shift = False

        url_field1 = Mock()
        url_field2 = Mock()
        mock_tab_manager.manager.tabs = [
            {"url_field": url_field1},
            {"url_field": url_field2}
        ]
        mock_tab_manager.manager.index = 1  # Second tab

        shortcuts.on_keyboard(event)

        url_field1.focus.assert_not_called()
        url_field2.focus.assert_called_once()

    def test_single_tab_cycling(self, shortcuts, mock_tab_manager):
        """Test tab cycling with only one tab."""
        event = Mock()
        event.ctrl = True
        event.meta = False
        event.key = "Tab"
        event.shift = False

        mock_tab_manager.manager.index = 0
        mock_tab_manager.manager.tabs = [Mock()]  # Only 1 tab

        shortcuts.on_keyboard(event)

        mock_tab_manager.select_tab.assert_called_once_with(0)  # Stay on same tab
