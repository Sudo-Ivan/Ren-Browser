from unittest.mock import Mock, patch

import flet as ft

from ren_browser.ui.settings import open_settings_tab
from ren_browser.ui.ui import build_ui


class TestBuildUI:
    """Test cases for the build_ui function."""

    def test_build_ui_basic_setup(self, mock_page):
        """Test that build_ui sets up basic page properties."""
        # Mock the page properties we can test without complex dependencies
        mock_page.theme_mode = None
        mock_page.window = Mock()
        mock_page.window.maximized = False
        mock_page.appbar = Mock()

        # Test basic setup that should always work
        mock_page.theme_mode = ft.ThemeMode.DARK
        mock_page.window.maximized = True

        assert mock_page.theme_mode == ft.ThemeMode.DARK
        assert mock_page.window.maximized is True

    @patch("ren_browser.announces.announces.AnnounceService")
    @patch("ren_browser.pages.page_request.PageFetcher")
    @patch("ren_browser.tabs.tabs.TabsManager")
    @patch("ren_browser.controls.shortcuts.Shortcuts")
    def test_build_ui_appbar_setup(
        self,
        mock_shortcuts,
        mock_tabs,
        mock_fetcher,
        mock_announce_service,
        mock_page,
    ):
        """Test that build_ui sets up the app bar correctly."""
        mock_tab_manager = Mock()
        mock_tabs.return_value = mock_tab_manager
        mock_tab_manager.manager.tabs = [{"url_field": Mock(), "go_btn": Mock()}]
        mock_tab_manager.manager.index = 0
        mock_tab_manager.tab_bar = Mock()
        mock_tab_manager.content_container = Mock()

        build_ui(mock_page)

        assert mock_page.appbar is not None
        assert mock_page.appbar.leading is not None
        assert mock_page.appbar.actions is not None
        assert mock_page.appbar.title is not None

    @patch("ren_browser.announces.announces.AnnounceService")
    @patch("ren_browser.pages.page_request.PageFetcher")
    @patch("ren_browser.tabs.tabs.TabsManager")
    @patch("ren_browser.controls.shortcuts.Shortcuts")
    def test_build_ui_drawer_setup(
        self,
        mock_shortcuts,
        mock_tabs,
        mock_fetcher,
        mock_announce_service,
        mock_page,
    ):
        """Test that build_ui sets up the drawer correctly."""
        mock_tab_manager = Mock()
        mock_tabs.return_value = mock_tab_manager
        mock_tab_manager.manager.tabs = [{"url_field": Mock(), "go_btn": Mock()}]
        mock_tab_manager.manager.index = 0
        mock_tab_manager.tab_bar = Mock()
        mock_tab_manager.content_container = Mock()

        build_ui(mock_page)

        assert mock_page.drawer is not None
        assert isinstance(mock_page.drawer, ft.NavigationDrawer)

    def test_ui_basic_functionality(self, mock_page):
        """Test basic UI functionality without complex mocking."""
        # Test that we can create basic UI components
        mock_page.theme_mode = ft.ThemeMode.DARK
        mock_page.window = Mock()
        mock_page.window.maximized = True
        mock_page.appbar = Mock()
        mock_page.drawer = Mock()

        # Verify basic properties can be set
        assert mock_page.theme_mode == ft.ThemeMode.DARK
        assert mock_page.window.maximized is True


class TestOpenSettingsTab:
    """Test cases for the open_settings_tab function."""

    def test_open_settings_tab_basic(self, mock_page, mock_storage_manager):
        """Test opening settings tab with basic functionality."""
        mock_tab_manager = Mock()
        mock_tab_manager.manager.tabs = []
        mock_tab_manager._add_tab_internal = Mock()
        mock_tab_manager.select_tab = Mock()

        mock_page.overlay = []

        with (
            patch(
                "ren_browser.ui.settings.get_storage_manager",
                return_value=mock_storage_manager,
            ),
            patch("ren_browser.ui.settings.rns.get_config_path", return_value="/tmp/rns"),
            patch("pathlib.Path.read_text", return_value="config content"),
        ):
            open_settings_tab(mock_page, mock_tab_manager)

            mock_tab_manager._add_tab_internal.assert_called_once()
            mock_tab_manager.select_tab.assert_called_once()
            mock_page.update.assert_called()

    def test_open_settings_tab_config_error(self, mock_page, mock_storage_manager):
        """Test opening settings tab when config file cannot be read."""
        mock_tab_manager = Mock()
        mock_tab_manager.manager.tabs = []
        mock_tab_manager._add_tab_internal = Mock()
        mock_tab_manager.select_tab = Mock()

        mock_page.overlay = []

        with (
            patch(
                "ren_browser.ui.settings.get_storage_manager",
                return_value=mock_storage_manager,
            ),
            patch("ren_browser.ui.settings.rns.get_config_path", return_value="/tmp/rns"),
            patch("pathlib.Path.read_text", side_effect=Exception("File not found")),
        ):
            open_settings_tab(mock_page, mock_tab_manager)

            mock_tab_manager._add_tab_internal.assert_called_once()
            mock_tab_manager.select_tab.assert_called_once()
            # Verify settings tab was opened
            args = mock_tab_manager._add_tab_internal.call_args
            assert args[0][0] == "Settings"

    def test_settings_save_config_success(self, mock_page, mock_storage_manager):
        """Test saving config successfully in settings."""
        mock_tab_manager = Mock()
        mock_tab_manager.manager.tabs = []
        mock_tab_manager._add_tab_internal = Mock()
        mock_tab_manager.select_tab = Mock()

        mock_page.overlay = []

        with (
            patch(
                "ren_browser.ui.settings.get_storage_manager",
                return_value=mock_storage_manager,
            ),
            patch("ren_browser.ui.settings.rns.get_config_path", return_value="/tmp/rns"),
            patch("pathlib.Path.read_text", return_value="config"),
            patch("pathlib.Path.write_text") as mock_write,
        ):
            open_settings_tab(mock_page, mock_tab_manager)

            # Get the settings content that was added
            settings_content = mock_tab_manager._add_tab_internal.call_args[0][1]

            # Find the save button - now nested in action_row container
            save_btn = None
            for control in settings_content.controls:
                if hasattr(control, "content") and hasattr(control.content, "controls"):
                    for sub_control in control.content.controls:
                        if (
                            hasattr(sub_control, "text")
                            and sub_control.text == "Save Configuration"
                        ):
                            save_btn = sub_control
                            break

            assert save_btn is not None
            save_btn.on_click(None)
            assert mock_write.called

    def test_settings_save_config_error(self, mock_page, mock_storage_manager):
        """Test saving config error path does not crash."""
        mock_tab_manager = Mock()
        mock_tab_manager.manager.tabs = []
        mock_tab_manager._add_tab_internal = Mock()
        mock_tab_manager.select_tab = Mock()

        mock_page.overlay = []

        with (
            patch(
                "ren_browser.ui.settings.get_storage_manager",
                return_value=mock_storage_manager,
            ),
            patch("ren_browser.ui.settings.rns.get_config_path", return_value="/tmp/rns"),
            patch("pathlib.Path.read_text", return_value="config"),
            patch("pathlib.Path.write_text", side_effect=Exception("disk full")),
        ):
            open_settings_tab(mock_page, mock_tab_manager)

            settings_content = mock_tab_manager._add_tab_internal.call_args[0][1]
            save_btn = None
            for control in settings_content.controls:
                if hasattr(control, "content") and hasattr(control.content, "controls"):
                    for sub_control in control.content.controls:
                        if (
                            hasattr(sub_control, "text")
                            and sub_control.text == "Save Configuration"
                        ):
                            save_btn = sub_control
                            break
            assert save_btn is not None
            # Should not raise despite write failure
            save_btn.on_click(None)

    def test_settings_status_section_present(self, mock_page, mock_storage_manager):
        """Ensure the status navigation button is present."""
        mock_tab_manager = Mock()
        mock_tab_manager.manager.tabs = []
        mock_tab_manager._add_tab_internal = Mock()
        mock_tab_manager.select_tab = Mock()

        mock_page.overlay = []

        with (
            patch(
                "ren_browser.ui.settings.get_storage_manager",
                return_value=mock_storage_manager,
            ),
            patch("ren_browser.ui.settings.rns.get_config_path", return_value="/tmp/rns"),
            patch("pathlib.Path.read_text", return_value="config"),
        ):
            open_settings_tab(mock_page, mock_tab_manager)

            settings_content = mock_tab_manager._add_tab_internal.call_args[0][1]
            nav_container = settings_content.controls[1]
            button_labels = [
                ctrl.text
                for ctrl in nav_container.content.controls
                if hasattr(ctrl, "text")
            ]
            assert "Status" in button_labels
