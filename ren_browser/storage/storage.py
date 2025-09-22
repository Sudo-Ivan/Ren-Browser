"""Cross-platform storage management for Ren Browser.

Provides persistent storage for configuration, bookmarks, history,
and other application data across different platforms.
"""

import json
import os
import pathlib
from typing import Any, Dict, Optional

import flet as ft


class StorageManager:
    """Cross-platform storage manager for Ren Browser.

    Handles configuration, bookmarks, history, and other persistent data
    with platform-specific storage locations.
    """

    def __init__(self, page: Optional[ft.Page] = None):
        """Initialize storage manager.

        Args:
            page: Optional Flet page instance for client storage access.

        """
        self.page = page
        self._storage_dir = self._get_storage_directory()
        self._ensure_storage_directory()

    def _get_storage_directory(self) -> pathlib.Path:
        """Get the appropriate storage directory for the current platform."""
        # Try to use Flet's client storage if available (works on all platforms)
        if self.page and hasattr(self.page, "client_storage"):
            pass

        if os.name == "posix" and "ANDROID_ROOT" in os.environ:
            # Android - use app's private files directory
            storage_dir = pathlib.Path("/data/data/com.ren_browser/files")
        elif hasattr(os, "uname") and "iOS" in str(
            getattr(os, "uname", lambda: "")()
        ).replace("iPhone", "iOS"):
            # iOS - use app's documents directory
            storage_dir = pathlib.Path.home() / "Documents" / "ren_browser"
        else:
            # Desktop (Linux, Windows, macOS) - use home directory
            if "APPDATA" in os.environ:  # Windows
                storage_dir = pathlib.Path(os.environ["APPDATA"]) / "ren_browser"
            elif "XDG_CONFIG_HOME" in os.environ:  # Linux XDG standard
                storage_dir = (
                    pathlib.Path(os.environ["XDG_CONFIG_HOME"]) / "ren_browser"
                )
            else:
                storage_dir = pathlib.Path.home() / ".ren_browser"

        return storage_dir

    def _ensure_storage_directory(self):
        """Ensure the storage directory exists."""
        try:
            self._storage_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            import tempfile

            self._storage_dir = pathlib.Path(tempfile.gettempdir()) / "ren_browser"
            self._storage_dir.mkdir(parents=True, exist_ok=True)

    def get_config_path(self) -> pathlib.Path:
        """Get the path to the main configuration file."""
        return self._storage_dir / "config"

    def get_reticulum_config_path(self) -> pathlib.Path:
        """Get the path to the Reticulum configuration directory."""
        # Check for global override from app
        try:
            from ren_browser.app import RNS_CONFIG_DIR

            if RNS_CONFIG_DIR:
                return pathlib.Path(RNS_CONFIG_DIR)
        except ImportError:
            pass

        # On Android, use app storage directory instead of ~/.reticulum
        if os.name == "posix" and "ANDROID_ROOT" in os.environ:
            return self._storage_dir / "reticulum"

        # Default to standard RNS config directory
        return pathlib.Path.home() / ".reticulum"

    def save_config(self, config_content: str) -> bool:
        """Save configuration content to file.

        Args:
            config_content: Configuration text to save

        Returns:
            True if successful, False otherwise

        """
        try:
            # Always save to client storage first (most reliable on mobile)
            if self.page and hasattr(self.page, "client_storage"):
                self.page.client_storage.set("ren_browser_config", config_content)

            # Save to reticulum config directory for RNS to use
            reticulum_config_path = self.get_reticulum_config_path() / "config"
            reticulum_config_path.parent.mkdir(parents=True, exist_ok=True)
            reticulum_config_path.write_text(config_content, encoding="utf-8")

            # Also save to local config path as backup
            config_path = self.get_config_path()
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content, encoding="utf-8")
            return True

        except (OSError, PermissionError, UnicodeEncodeError) as e:
            return self._save_config_fallback(config_content, str(e))

    def _save_config_fallback(self, config_content: str, error: str) -> bool:
        """Fallback config saving for when primary method fails."""
        try:
            if self.page and hasattr(self.page, "client_storage"):
                self.page.client_storage.set("ren_browser_config", config_content)
                self.page.client_storage.set(
                    "ren_browser_config_error", f"File save failed: {error}"
                )
                return True

            try:
                reticulum_config_path = self.get_reticulum_config_path() / "config"
                reticulum_config_path.write_text(config_content, encoding="utf-8")
                return True
            except (OSError, PermissionError):
                pass

            import tempfile

            temp_path = pathlib.Path(tempfile.gettempdir()) / "ren_browser_config.txt"
            temp_path.write_text(config_content, encoding="utf-8")
            return True

        except Exception:
            return False

    def load_config(self) -> str:
        """Load configuration content from storage.

        Returns:
            Configuration text, or empty string if not found

        """
        # On Android, prioritize client storage first as it's more reliable
        if os.name == "posix" and "ANDROID_ROOT" in os.environ:
            if self.page and hasattr(self.page, "client_storage"):
                stored_config = self.page.client_storage.get("ren_browser_config")
                if stored_config:
                    return stored_config

        try:
            reticulum_config_path = self.get_reticulum_config_path() / "config"
            if reticulum_config_path.exists():
                return reticulum_config_path.read_text(encoding="utf-8")

            config_path = self.get_config_path()
            if config_path.exists():
                return config_path.read_text(encoding="utf-8")

            # Fallback to client storage for non-Android or if files don't exist
            if self.page and hasattr(self.page, "client_storage"):
                stored_config = self.page.client_storage.get("ren_browser_config")
                if stored_config:
                    return stored_config

        except (OSError, PermissionError, UnicodeDecodeError):
            # If file access fails, try client storage as fallback
            if self.page and hasattr(self.page, "client_storage"):
                stored_config = self.page.client_storage.get("ren_browser_config")
                if stored_config:
                    return stored_config

        return ""

    def save_bookmarks(self, bookmarks: list) -> bool:
        """Save bookmarks to storage."""
        try:
            bookmarks_path = self._storage_dir / "bookmarks.json"
            with open(bookmarks_path, "w", encoding="utf-8") as f:
                json.dump(bookmarks, f, indent=2)

            if self.page and hasattr(self.page, "client_storage"):
                self.page.client_storage.set(
                    "ren_browser_bookmarks", json.dumps(bookmarks)
                )

            return True
        except Exception:
            return False

    def load_bookmarks(self) -> list:
        """Load bookmarks from storage."""
        try:
            bookmarks_path = self._storage_dir / "bookmarks.json"
            if bookmarks_path.exists():
                with open(bookmarks_path, "r", encoding="utf-8") as f:
                    return json.load(f)

            if self.page and hasattr(self.page, "client_storage"):
                stored_bookmarks = self.page.client_storage.get("ren_browser_bookmarks")
                if stored_bookmarks:
                    return json.loads(stored_bookmarks)

        except (OSError, json.JSONDecodeError):
            pass

        return []

    def save_history(self, history: list) -> bool:
        """Save browsing history to storage."""
        try:
            history_path = self._storage_dir / "history.json"
            with open(history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)

            if self.page and hasattr(self.page, "client_storage"):
                self.page.client_storage.set("ren_browser_history", json.dumps(history))

            return True
        except Exception:
            return False

    def load_history(self) -> list:
        """Load browsing history from storage."""
        try:
            history_path = self._storage_dir / "history.json"
            if history_path.exists():
                with open(history_path, "r", encoding="utf-8") as f:
                    return json.load(f)

            if self.page and hasattr(self.page, "client_storage"):
                stored_history = self.page.client_storage.get("ren_browser_history")
                if stored_history:
                    return json.loads(stored_history)

        except (OSError, json.JSONDecodeError):
            pass

        return []

    def get_storage_info(self) -> Dict[str, Any]:
        """Get information about the storage system."""
        return {
            "storage_dir": str(self._storage_dir),
            "config_path": str(self.get_config_path()),
            "reticulum_config_path": str(self.get_reticulum_config_path()),
            "storage_dir_exists": self._storage_dir.exists(),
            "storage_dir_writable": self._is_writable(self._storage_dir),
            "has_client_storage": self.page and hasattr(self.page, "client_storage"),
        }

    @staticmethod
    def _is_writable(path: pathlib.Path) -> bool:
        """Check if a directory is writable."""
        try:
            test_file = path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except (OSError, PermissionError):
            return False


# Global storage instance
_storage_manager: Optional[StorageManager] = None


def get_storage_manager(page: Optional[ft.Page] = None) -> StorageManager:
    """Get the global storage manager instance."""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager(page)
    elif page and _storage_manager.page is None:
        _storage_manager.page = page
    return _storage_manager


def initialize_storage(page: ft.Page) -> StorageManager:
    """Initialize the storage system with a Flet page."""
    global _storage_manager
    _storage_manager = StorageManager(page)
    return _storage_manager


def get_rns_config_directory() -> str:
    """Get the RNS config directory, checking for global override."""
    try:
        from ren_browser.app import RNS_CONFIG_DIR

        if RNS_CONFIG_DIR:
            return RNS_CONFIG_DIR
    except ImportError:
        pass

    # Default to standard RNS config directory
    return str(pathlib.Path.home() / ".reticulum")
