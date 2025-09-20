from unittest.mock import MagicMock, Mock

import flet as ft
import pytest


@pytest.fixture
def mock_page():
    """Create a mock Flet page for testing."""
    page = Mock(spec=ft.Page)
    page.add = Mock()
    page.update = Mock()
    page.run_thread = Mock()
    page.controls = []
    page.theme_mode = ft.ThemeMode.DARK
    page.appbar = Mock()
    page.drawer = Mock()
    page.window = Mock()
    page.width = 1024
    page.snack_bar = None
    page.on_resized = None
    page.on_keyboard_event = None
    return page


@pytest.fixture
def mock_rns():
    """Mock RNS module to avoid network dependencies in tests."""
    mock_rns = MagicMock()
    mock_rns.Reticulum = Mock()
    mock_rns.Transport = Mock()
    mock_rns.Identity = Mock()
    mock_rns.Destination = Mock()
    mock_rns.Link = Mock()
    mock_rns.log = Mock()

    # Mock at the module level for all imports
    import sys
    sys.modules["RNS"] = mock_rns

    yield mock_rns

    # Cleanup
    if "RNS" in sys.modules:
        del sys.modules["RNS"]


@pytest.fixture
def sample_announce_data():
    """Sample announce data for testing."""
    return {
        "destination_hash": "1234567890abcdef",
        "display_name": "Test Node",
        "timestamp": 1234567890
    }


@pytest.fixture
def sample_page_request():
    """Sample page request for testing."""
    from ren_browser.pages.page_request import PageRequest
    return PageRequest(
        destination_hash="1234567890abcdef",
        page_path="/page/index.mu",
        field_data=None
    )


@pytest.fixture
def mock_storage_manager():
    """Mock storage manager for testing."""
    mock_storage = Mock()
    mock_storage.load_config.return_value = "test config content"
    mock_storage.save_config.return_value = True
    mock_storage.get_config_path.return_value = Mock()
    mock_storage.get_reticulum_config_path.return_value = Mock()
    mock_storage.get_storage_info.return_value = {
        'storage_dir': '/mock/storage',
        'config_path': '/mock/storage/config.txt',
        'reticulum_config_path': '/mock/storage/reticulum',
        'storage_dir_exists': True,
        'storage_dir_writable': True,
        'has_client_storage': True,
    }
    return mock_storage
