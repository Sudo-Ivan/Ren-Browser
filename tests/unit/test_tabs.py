from types import SimpleNamespace
from unittest.mock import Mock, patch

import flet as ft
import pytest

from ren_browser.tabs.tabs import TabsManager


class TestTabsManager:
    """Test cases for the TabsManager class."""

    @pytest.fixture
    def tabs_manager(self, mock_page):
        """Create a TabsManager instance for testing."""
        mock_page.width = 800  # Simulate page width for adaptive logic
        with (
            patch("ren_browser.app.RENDERER", "plaintext"),
            patch("ren_browser.renderer.plaintext.render_plaintext") as mock_render,
        ):
            mock_render.return_value = Mock(spec=ft.Text)
            return TabsManager(mock_page)

    def test_tabs_manager_init(self, mock_page):
        """Test TabsManager initialization."""
        with (
            patch("ren_browser.app.RENDERER", "plaintext"),
            patch("ren_browser.renderer.plaintext.render_plaintext") as mock_render,
        ):
            mock_render.return_value = Mock(spec=ft.Text)
            manager = TabsManager(mock_page)

            assert manager.page == mock_page
            assert isinstance(manager.manager, SimpleNamespace)
            assert len(manager.manager.tabs) == 1
            assert manager.manager.index == 0
            assert isinstance(manager.tab_bar, ft.Container)
            assert isinstance(manager.tab_bar.content, ft.Row)
            assert manager.overflow_menu is None
            assert isinstance(manager.content_container, ft.Container)

    def test_tabs_manager_init_micron_renderer(self, mock_page):
        """Test TabsManager initialization with micron renderer."""
        with patch("ren_browser.app.RENDERER", "micron"):
            manager = TabsManager(mock_page)

            # Verify that micron renderer was selected and TabsManager was created
            assert manager.page == mock_page
            assert len(manager.manager.tabs) == 1

    def test_add_tab_internal(self, tabs_manager):
        """Test adding a tab internally."""
        content = Mock(spec=ft.Text)
        tabs_manager._add_tab_internal("Test Tab", content)

        assert len(tabs_manager.manager.tabs) == 2
        new_tab = tabs_manager.manager.tabs[1]
        assert new_tab["title"] == "Test Tab"
        assert new_tab["content_control"] == content

    def test_on_add_click(self, tabs_manager):
        """Test adding a new tab via button click."""
        with (
            patch("ren_browser.app.RENDERER", "plaintext"),
            patch("ren_browser.renderer.plaintext.render_plaintext") as mock_render,
        ):
            mock_render.return_value = Mock(spec=ft.Text)
            initial_count = len(tabs_manager.manager.tabs)

            tabs_manager._on_add_click(None)

            assert len(tabs_manager.manager.tabs) == initial_count + 1
            assert tabs_manager.manager.index == initial_count
            tabs_manager.page.update.assert_called()

    def test_on_close_click_multiple_tabs(self, tabs_manager):
        """Test closing a tab when multiple tabs exist."""
        tabs_manager._add_tab_internal("Tab 2", Mock())
        tabs_manager._add_tab_internal("Tab 3", Mock())
        tabs_manager.select_tab(1)

        initial_count = len(tabs_manager.manager.tabs)
        tabs_manager._on_close_click(None)

        assert len(tabs_manager.manager.tabs) == initial_count - 1
        tabs_manager.page.update.assert_called()

    def test_on_close_click_single_tab(self, tabs_manager):
        """Test closing a tab when only one tab exists (should not close)."""
        initial_count = len(tabs_manager.manager.tabs)
        tabs_manager._on_close_click(None)

        assert len(tabs_manager.manager.tabs) == initial_count

    def test_select_tab(self, tabs_manager):
        """Test selecting a tab."""
        tabs_manager._add_tab_internal("Tab 2", Mock())

        tabs_manager.select_tab(1)

        assert tabs_manager.manager.index == 1
        tabs_manager.page.update.assert_called()

    def test_select_tab_updates_background_colors(self, tabs_manager):
        """Test that selecting a tab updates background colors correctly."""
        tabs_manager._add_tab_internal("Tab 2", Mock())

        tab_controls = tabs_manager.tab_bar.content.controls[
            :-2
        ]  # Exclude add/close buttons

        tabs_manager.select_tab(1)

        assert tab_controls[0].bgcolor == ft.Colors.GREY_800
        assert tab_controls[1].bgcolor == ft.Colors.BLUE_900

    def test_on_tab_go_empty_url(self, tabs_manager):
        """Test tab go with empty URL."""
        tab = tabs_manager.manager.tabs[0]
        tab["url_field"].value = ""

        tabs_manager._on_tab_go(None, 0)

        # Should not change anything for empty URL
        assert len(tabs_manager.manager.tabs) == 1

    def test_on_tab_go_with_url(self, tabs_manager):
        """Test tab go with valid URL."""
        tab = tabs_manager.manager.tabs[0]
        tab["url_field"].value = "test://example"

        tabs_manager._on_tab_go(None, 0)

        # Verify that the tab content was updated and page was refreshed
        tabs_manager.page.update.assert_called()

    def test_on_tab_go_micron_renderer(self, tabs_manager):
        """Test tab go with micron renderer."""
        with patch("ren_browser.app.RENDERER", "micron"):
            tab = tabs_manager.manager.tabs[0]
            tab["url_field"].value = "test://example"

            tabs_manager._on_tab_go(None, 0)

            # Verify that the page was updated with micron renderer
            tabs_manager.page.update.assert_called()

    def test_tab_container_properties(self, tabs_manager):
        """Test that tab container has correct properties."""
        assert tabs_manager.content_container.expand is True
        assert tabs_manager.content_container.bgcolor in (ft.Colors.BLACK, "#000000")
        assert tabs_manager.content_container.padding == ft.padding.all(16)

    def test_tab_bar_controls(self, tabs_manager):
        """Test that tab bar has correct controls."""
        controls = tabs_manager.tab_bar.content.controls

        # Should have: home tab, add button, close button (and potentially overflow menu)
        assert len(controls) >= 3
        assert isinstance(controls[-2], ft.IconButton)  # Add button
        assert isinstance(controls[-1], ft.IconButton)  # Close button
        assert controls[-2].icon == ft.Icons.ADD
        assert controls[-1].icon == ft.Icons.CLOSE

    def test_tab_content_structure(self, tabs_manager):
        """Test the structure of tab content."""
        tab = tabs_manager.manager.tabs[0]

        assert "title" in tab
        assert "url_field" in tab
        assert "go_btn" in tab
        assert "content_control" in tab
        assert "content" in tab

        assert isinstance(tab["url_field"], ft.TextField)
        assert isinstance(tab["go_btn"], ft.IconButton)
        assert isinstance(tab["content"], ft.Column)

    def test_url_field_properties(self, tabs_manager):
        """Test URL field properties."""
        tab = tabs_manager.manager.tabs[0]
        url_field = tab["url_field"]

        assert url_field.expand is True
        assert url_field.text_style.size == 14
        assert url_field.content_padding is not None

    def test_go_button_properties(self, tabs_manager):
        """Test go button properties."""
        tab = tabs_manager.manager.tabs[0]
        go_btn = tab["go_btn"]

        assert go_btn.icon == ft.Icons.ARROW_FORWARD
        assert go_btn.tooltip == "Go"

    def test_tab_click_handlers(self, tabs_manager):
        """Test that tab click handlers are properly set."""
        tabs_manager._add_tab_internal("Tab 2", Mock())

        tab_controls = tabs_manager.tab_bar.content.controls[
            :-2
        ]  # Exclude add/close buttons

        for i, control in enumerate(tab_controls):
            assert control.on_click is not None

    def test_multiple_tabs_management(self, tabs_manager):
        """Test management of multiple tabs."""
        # Add several tabs
        for i in range(3):
            tabs_manager._add_tab_internal(f"Tab {i + 2}", Mock())

        assert len(tabs_manager.manager.tabs) == 4

        # Select different tabs
        tabs_manager.select_tab(2)
        assert tabs_manager.manager.index == 2

        # Close current tab
        tabs_manager._on_close_click(None)
        assert len(tabs_manager.manager.tabs) == 3
        assert tabs_manager.manager.index <= 2

    def test_tab_content_update_on_select(self, tabs_manager):
        """Test that content container updates when selecting tabs."""
        content1 = Mock()
        content2 = Mock()

        tabs_manager._add_tab_internal("Tab 2", content1)
        tabs_manager._add_tab_internal("Tab 3", content2)

        tabs_manager.select_tab(1)
        assert (
            tabs_manager.content_container.content
            == tabs_manager.manager.tabs[1]["content"]
        )

        tabs_manager.select_tab(2)
        assert (
            tabs_manager.content_container.content
            == tabs_manager.manager.tabs[2]["content"]
        )

    def test_adaptive_overflow_behavior(self, tabs_manager):
        """Test that the overflow menu adapts to tab changes."""
        # With page width at 800, add enough tabs that some should overflow.
        for i in range(10):  # Total 11 tabs
            tabs_manager._add_tab_internal(f"Tab {i + 2}", Mock())

        # Check that an overflow menu exists
        assert tabs_manager.overflow_menu is not None

        # Simulate a smaller screen, expecting more tabs to overflow
        tabs_manager.page.width = 400
        tabs_manager._update_tab_visibility()
        visible_tabs_small = sum(
            1
            for c in tabs_manager.tab_bar.content.controls
            if isinstance(c, ft.Container) and c.visible
        )
        assert visible_tabs_small < 11

        # Simulate a larger screen, expecting all tabs to be visible
        tabs_manager.page.width = 1600
        tabs_manager._update_tab_visibility()
        visible_tabs_large = sum(
            1
            for c in tabs_manager.tab_bar.content.controls
            if isinstance(c, ft.Container) and c.visible
        )

        assert visible_tabs_large == 11
        assert tabs_manager.overflow_menu is None
