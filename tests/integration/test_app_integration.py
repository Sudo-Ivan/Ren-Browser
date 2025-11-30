from unittest.mock import Mock

import flet as ft
import pytest

from ren_browser import app


class TestAppIntegration:
    """Integration tests for the main app functionality."""

    @pytest.mark.asyncio
    async def test_main_function_structure(self):
        """Test that the main function has the expected structure."""
        mock_page = Mock()
        mock_page.add = Mock()
        mock_page.update = Mock()
        mock_page.controls = Mock()
        mock_page.controls.clear = Mock()
        mock_page.width = 1024
        mock_page.window = Mock()
        mock_page.window.maximized = False
        mock_page.appbar = Mock()
        mock_page.drawer = Mock()
        mock_page.theme_mode = ft.ThemeMode.DARK

        await app.main(mock_page)

        assert mock_page.add.call_count >= 1
        loader_call = mock_page.add.call_args_list[0][0][0]
        assert isinstance(loader_call, ft.Container)
        mock_page.update.assert_called()

    def test_entry_points_exist(self):
        """Test that all expected entry points exist and are callable."""
        entry_points = [
            "run",
            "web",
            "android",
            "ios",
            "run_dev",
            "web_dev",
            "android_dev",
            "ios_dev",
        ]

        for entry_point in entry_points:
            assert hasattr(app, entry_point)
            assert callable(getattr(app, entry_point))

    def test_renderer_global_exists(self):
        """Test that the RENDERER global variable exists."""
        assert hasattr(app, "RENDERER")
        assert app.RENDERER in ["plaintext", "micron"]

    def test_app_module_imports(self):
        """Test that required modules can be imported."""
        # Test that the app module imports work
        import ren_browser.app
        import ren_browser.ui.ui

        # Verify key functions exist
        assert hasattr(ren_browser.app, "main")
        assert hasattr(ren_browser.app, "run")
        assert hasattr(ren_browser.ui.ui, "build_ui")


class TestModuleIntegration:
    """Integration tests for module interactions."""

    def test_renderer_modules_exist(self):
        """Test that renderer modules can be imported."""
        from ren_browser.renderer import micron, plaintext

        assert hasattr(plaintext, "render_plaintext")
        assert hasattr(micron, "render_micron")
        assert callable(plaintext.render_plaintext)
        assert callable(micron.render_micron)

    def test_data_classes_exist(self):
        """Test that data classes can be imported and used."""
        from ren_browser.announces.announces import Announce
        from ren_browser.pages.page_request import PageRequest

        # Test Announce creation
        announce = Announce("hash1", "name1", 1000)
        assert announce.destination_hash == "hash1"

        # Test PageRequest creation
        request = PageRequest("hash2", "/path")
        assert request.destination_hash == "hash2"

    def test_logs_module_integration(self):
        """Test that logs module integrates correctly."""
        from ren_browser import logs

        # Test that log functions exist
        assert hasattr(logs, "log_error")
        assert hasattr(logs, "log_app")
        assert hasattr(logs, "log_ret")

        # Test that log storage exists
        assert hasattr(logs, "APP_LOGS")
        assert hasattr(logs, "ERROR_LOGS")
        assert hasattr(logs, "RET_LOGS")

        # Test that they are lists
        assert isinstance(logs.APP_LOGS, list)
        assert isinstance(logs.ERROR_LOGS, list)
        assert isinstance(logs.RET_LOGS, list)
