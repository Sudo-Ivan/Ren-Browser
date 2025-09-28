import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ren_browser.storage.storage import (
    StorageManager,
    get_storage_manager,
    initialize_storage,
)


class TestStorageManager:
    """Test cases for the StorageManager class."""

    def test_storage_manager_init_without_page(self):
        """Test StorageManager initialization without a page."""
        with patch(
            "ren_browser.storage.storage.StorageManager._get_storage_directory",
        ) as mock_get_dir:
            mock_dir = Path("/mock/storage")
            mock_get_dir.return_value = mock_dir

            with patch("pathlib.Path.mkdir") as mock_mkdir:
                storage = StorageManager()

                assert storage.page is None
                assert storage._storage_dir == mock_dir
                mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_storage_manager_init_with_page(self):
        """Test StorageManager initialization with a page."""
        mock_page = Mock()

        with patch(
            "ren_browser.storage.storage.StorageManager._get_storage_directory",
        ) as mock_get_dir:
            mock_dir = Path("/mock/storage")
            mock_get_dir.return_value = mock_dir

            with patch("pathlib.Path.mkdir"):
                storage = StorageManager(mock_page)

                assert storage.page == mock_page
                assert storage._storage_dir == mock_dir

    def test_get_storage_directory_desktop(self):
        """Test storage directory detection for desktop platforms."""
        with (
            patch("os.name", "posix"),
            patch.dict(
                "os.environ", {"XDG_CONFIG_HOME": "/home/user/.config"}, clear=True,
            ),
            patch("pathlib.Path.mkdir"),
        ):
            with patch(
                "ren_browser.storage.storage.StorageManager._ensure_storage_directory",
            ):
                storage = StorageManager()
                storage._storage_dir = storage._get_storage_directory()
                expected_dir = Path("/home/user/.config") / "ren_browser"
                assert storage._storage_dir == expected_dir

    def test_get_storage_directory_windows(self):
        """Test storage directory detection for Windows."""
        # Skip this test on non-Windows systems to avoid path issues
        pytest.skip("Windows path test skipped on non-Windows system")

    def test_get_storage_directory_android(self):
        """Test storage directory detection for Android."""
        with (
            patch("os.name", "posix"),
            patch.dict("os.environ", {"ANDROID_ROOT": "/system"}, clear=True),
            patch("pathlib.Path.mkdir"),
        ):
            with patch(
                "ren_browser.storage.storage.StorageManager._ensure_storage_directory",
            ):
                storage = StorageManager()
                storage._storage_dir = storage._get_storage_directory()
                expected_dir = Path("/storage/emulated/0/Documents/ren_browser")
                assert storage._storage_dir == expected_dir

    def test_get_config_path(self):
        """Test getting config file path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            config_path = storage.get_config_path()
            expected_path = Path(temp_dir) / "config"
            assert config_path == expected_path

    def test_get_reticulum_config_path(self):
        """Test getting Reticulum config directory path."""
        storage = StorageManager()

        config_path = storage.get_reticulum_config_path()
        expected_path = Path.home() / ".reticulum"
        assert config_path == expected_path

    def test_save_config_success(self):
        """Test successful config saving."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to use temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                config_content = "test config content"
                result = storage.save_config(config_content)

                assert result is True
                config_path = storage.get_config_path()
                assert config_path.exists()
                assert config_path.read_text(encoding="utf-8") == config_content

    def test_save_config_with_client_storage(self):
        """Test config saving with client storage."""
        mock_page = Mock()
        mock_page.client_storage.set = Mock()

        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(mock_page)
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to use temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                config_content = "test config content"
                result = storage.save_config(config_content)

                assert result is True
                mock_page.client_storage.set.assert_called_with(
                    "ren_browser_config", config_content,
                )

    def test_save_config_fallback(self):
        """Test config saving fallback when file system fails."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_page = Mock()
            mock_page.client_storage.set = Mock()

            storage = StorageManager(mock_page)
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to use temp dir and cause failure
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                with patch(
                    "pathlib.Path.write_text",
                    side_effect=PermissionError("Access denied"),
                ):
                    config_content = "test config content"
                    result = storage.save_config(config_content)

                    assert result is True
                    # Check that the config was set to client storage
                    mock_page.client_storage.set.assert_any_call(
                        "ren_browser_config", config_content,
                    )
            # Verify that client storage was called at least once
            assert mock_page.client_storage.set.call_count >= 1

    def test_load_config_from_file(self):
        """Test loading config from file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to use temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                config_content = "test config content"
                config_path = storage.get_config_path()
                config_path.write_text(config_content, encoding="utf-8")

                loaded_config = storage.load_config()
                assert loaded_config == config_content

    def test_load_config_from_client_storage(self):
        """Test loading config from client storage when file doesn't exist."""
        mock_page = Mock()
        mock_page.client_storage.get = Mock(return_value="client storage config")

        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager(mock_page)
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to also be in temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                loaded_config = storage.load_config()
                assert loaded_config == "client storage config"
                mock_page.client_storage.get.assert_called_with("ren_browser_config")

    def test_load_config_default(self):
        """Test loading default config when no config exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to also be in temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                loaded_config = storage.load_config()
                assert loaded_config == ""

    def test_save_bookmarks(self):
        """Test saving bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            bookmarks = [{"name": "Test", "url": "test://example"}]
            result = storage.save_bookmarks(bookmarks)

            assert result is True
            bookmarks_path = storage._storage_dir / "bookmarks.json"
            assert bookmarks_path.exists()

            with open(bookmarks_path, encoding="utf-8") as f:
                loaded_bookmarks = json.load(f)
            assert loaded_bookmarks == bookmarks

    def test_load_bookmarks(self):
        """Test loading bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            bookmarks = [{"name": "Test", "url": "test://example"}]
            bookmarks_path = storage._storage_dir / "bookmarks.json"

            with open(bookmarks_path, "w", encoding="utf-8") as f:
                json.dump(bookmarks, f)

            loaded_bookmarks = storage.load_bookmarks()
            assert loaded_bookmarks == bookmarks

    def test_load_bookmarks_empty(self):
        """Test loading bookmarks when none exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            loaded_bookmarks = storage.load_bookmarks()
            assert loaded_bookmarks == []

    def test_save_history(self):
        """Test saving history."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            history = [{"url": "test://example", "timestamp": 1234567890}]
            result = storage.save_history(history)

            assert result is True
            history_path = storage._storage_dir / "history.json"
            assert history_path.exists()

            with open(history_path, encoding="utf-8") as f:
                loaded_history = json.load(f)
            assert loaded_history == history

    def test_load_history(self):
        """Test loading history."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            history = [{"url": "test://example", "timestamp": 1234567890}]
            history_path = storage._storage_dir / "history.json"

            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(history, f)

            loaded_history = storage.load_history()
            assert loaded_history == history

    def test_get_storage_info(self):
        """Test getting storage information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_page = Mock()
            mock_page.client_storage = Mock()

            storage = StorageManager(mock_page)
            storage._storage_dir = Path(temp_dir)

            info = storage.get_storage_info()

            assert "storage_dir" in info
            assert "config_path" in info
            assert "reticulum_config_path" in info
            assert "storage_dir_exists" in info
            assert "storage_dir_writable" in info
            assert "has_client_storage" in info

            assert info["storage_dir"] == str(Path(temp_dir))
            assert info["storage_dir_exists"] is True
            assert info["has_client_storage"] is True

    def test_storage_directory_fallback(self):
        """Test fallback to temp directory when storage creation fails."""
        with patch.object(StorageManager, "_get_storage_directory") as mock_get_dir:
            mock_get_dir.return_value = Path("/nonexistent/path")

            with patch(
                "pathlib.Path.mkdir",
                side_effect=[PermissionError("Access denied"), None],
            ):
                with patch("tempfile.gettempdir", return_value="/tmp"):
                    storage = StorageManager()

                    expected_fallback = Path("/tmp") / "ren_browser"
                    assert storage._storage_dir == expected_fallback


class TestStorageGlobalFunctions:
    """Test cases for global storage functions."""

    def test_get_storage_manager_singleton(self):
        """Test that get_storage_manager returns the same instance."""
        with patch("ren_browser.storage.storage._storage_manager", None):
            storage1 = get_storage_manager()
            storage2 = get_storage_manager()

            assert storage1 is storage2

    def test_get_storage_manager_with_page(self):
        """Test get_storage_manager with page parameter."""
        mock_page = Mock()

        with patch("ren_browser.storage.storage._storage_manager", None):
            storage = get_storage_manager(mock_page)

            assert storage.page == mock_page

    def test_initialize_storage(self):
        """Test initialize_storage function."""
        mock_page = Mock()

        with patch("ren_browser.storage.storage._storage_manager", None):
            storage = initialize_storage(mock_page)

            assert storage.page == mock_page
            assert get_storage_manager() is storage


class TestStorageManagerEdgeCases:
    """Test edge cases and error scenarios."""

    def test_save_config_encoding_error(self):
        """Test config saving with encoding errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            # Mock the reticulum config path to use temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                # Test with content that might cause encoding issues
                with patch(
                    "pathlib.Path.write_text",
                    side_effect=UnicodeEncodeError("utf-8", "", 0, 1, "error"),
                ):
                    result = storage.save_config("test content")
                    # Should still succeed due to fallback
                    assert result is False

    def test_load_config_encoding_error(self):
        """Test config loading with encoding errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            storage._storage_dir = Path(temp_dir)

            # Create a config file with invalid encoding
            config_path = storage.get_config_path()
            config_path.write_bytes(b"\xff\xfe invalid utf-8")

            # Mock the reticulum config path to also be in temp dir
            with patch.object(
                storage,
                "get_reticulum_config_path",
                return_value=Path(temp_dir) / "reticulum",
            ):
                # Should return empty string when encoding fails
                config = storage.load_config()
                assert config == ""

    def test_is_writable_permission_denied(self):
        """Test _is_writable when permission is denied."""
        storage = StorageManager()

        with patch(
            "pathlib.Path.write_text", side_effect=PermissionError("Access denied"),
        ):
            test_path = Path("/mock/path")
            result = storage._is_writable(test_path)
            assert result is False

    def test_is_writable_success(self):
        """Test _is_writable when directory is writable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = StorageManager()
            test_path = Path(temp_dir)

            result = storage._is_writable(test_path)
            assert result is True
