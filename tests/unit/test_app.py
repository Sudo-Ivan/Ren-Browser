from unittest.mock import patch

import flet as ft
import pytest

from ren_browser import app


class TestApp:
    """Test cases for the main app module."""

    @pytest.mark.asyncio
    async def test_main_initializes_loader(self, mock_page, mock_rns):
        """Test that main function initializes with loading screen."""
        with (
            patch("ren_browser.rns.initialize_reticulum", return_value=True),
            patch("ren_browser.rns.get_reticulum_instance"),
            patch("ren_browser.rns.get_config_path", return_value="/tmp/.reticulum"),
            patch("ren_browser.app.build_ui"),
        ):
            await app.main(mock_page)

            assert mock_page.add.call_count >= 1
            loader_call = mock_page.add.call_args_list[0][0][0]
            assert isinstance(loader_call, ft.Container)
            mock_page.update.assert_called()

    @pytest.mark.asyncio
    async def test_main_function_structure(self, mock_page, mock_rns):
        """Test that main function sets up the expected structure."""
        with (
            patch("ren_browser.rns.initialize_reticulum", return_value=True),
            patch("ren_browser.rns.get_reticulum_instance"),
            patch("ren_browser.rns.get_config_path"),
            patch("ren_browser.app.build_ui"),
        ):
            await app.main(mock_page)

        assert mock_page.add.call_count >= 1
        loader_call = mock_page.add.call_args_list[0][0][0]
        assert isinstance(loader_call, ft.Container)
        mock_page.update.assert_called()

    def test_run_with_default_args(self, mock_rns):
        """Test run function with default arguments."""
        with patch("sys.argv", ["ren-browser"]), patch("flet.app") as mock_ft_app:
            app.run()

            mock_ft_app.assert_called_once()
            args = mock_ft_app.call_args
            assert args[0][0] == app.main

    def test_run_with_web_flag(self, mock_rns):
        """Test run function with web flag."""
        with (
            patch("sys.argv", ["ren-browser", "--web"]),
            patch("flet.app") as mock_ft_app,
        ):
            app.run()

            mock_ft_app.assert_called_once()
            args, kwargs = mock_ft_app.call_args
            assert args[0] == app.main
            assert kwargs["view"] == ft.AppView.WEB_BROWSER

    def test_run_with_web_and_port(self, mock_rns):
        """Test run function with web flag and custom port."""
        with (
            patch("sys.argv", ["ren-browser", "--web", "--port", "8080"]),
            patch("flet.app") as mock_ft_app,
        ):
            app.run()

            mock_ft_app.assert_called_once()
            args, kwargs = mock_ft_app.call_args
            assert args[0] == app.main
            assert kwargs["view"] == ft.AppView.WEB_BROWSER
            assert kwargs["port"] == 8080

    def test_run_with_renderer_flag(self, mock_rns):
        """Test run function with renderer selection."""
        with (
            patch("sys.argv", ["ren-browser", "--renderer", "micron"]),
            patch("flet.app"),
        ):
            app.run()

            assert app.RENDERER == "micron"

    def test_web_function(self, mock_rns):
        """Test web() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.web()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.WEB_BROWSER)

    def test_android_function(self, mock_rns):
        """Test android() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.android()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.FLET_APP_WEB)

    def test_ios_function(self, mock_rns):
        """Test ios() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.ios()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.FLET_APP_WEB)

    def test_run_dev_function(self, mock_rns):
        """Test run_dev() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.run_dev()

            mock_ft_app.assert_called_once_with(app.main)

    def test_web_dev_function(self, mock_rns):
        """Test web_dev() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.web_dev()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.WEB_BROWSER)

    def test_android_dev_function(self, mock_rns):
        """Test android_dev() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.android_dev()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.FLET_APP_WEB)

    def test_ios_dev_function(self, mock_rns):
        """Test ios_dev() entry point function."""
        with patch("flet.app") as mock_ft_app:
            app.ios_dev()

            mock_ft_app.assert_called_once_with(app.main, view=ft.AppView.FLET_APP_WEB)

    def test_global_renderer_setting(self):
        """Test that RENDERER global is properly updated."""
        original_renderer = app.RENDERER

        with (
            patch("sys.argv", ["ren-browser", "--renderer", "micron"]),
            patch("flet.app"),
        ):
            app.run()
            assert app.RENDERER == "micron"

        app.RENDERER = original_renderer
