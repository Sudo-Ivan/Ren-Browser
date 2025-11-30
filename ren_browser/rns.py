"""Reticulum helper utilities for Ren Browser."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

import RNS

logger = logging.getLogger(__name__)


class RNSManager:
    """Manage Reticulum lifecycle and configuration."""

    def __init__(self):
        self.reticulum = None
        self.config_path: str | None = None
        self.last_error: str | None = None

    def _is_android(self) -> bool:
        vendor = getattr(RNS, "vendor", None)
        platformutils = getattr(vendor, "platformutils", None)
        if platformutils and hasattr(platformutils, "is_android"):
            try:
                return bool(platformutils.is_android())
            except Exception:
                return False
        return "ANDROID_ROOT" in os.environ

    def _android_storage_root(self) -> Path:
        candidates = [
            os.environ.get("ANDROID_APP_PATH"),
            os.environ.get("ANDROID_PRIVATE"),
            os.environ.get("ANDROID_ARGUMENT"),
        ]
        for raw_path in candidates:
            if not raw_path:
                continue
            path = Path(raw_path).expanduser()
            if path.name == "app":
                path = path.parent
            if path.is_file():
                path = path.parent
            if path.is_dir():
                return path
        return Path(tempfile.gettempdir())

    def _default_config_root(self) -> Path:
        override = os.environ.get("REN_BROWSER_RNS_DIR") or os.environ.get(
            "REN_RETICULUM_CONFIG_DIR",
        )
        if override:
            return Path(override).expanduser()
        if self._is_android():
            return self._android_storage_root() / "ren_browser" / "reticulum"
        return Path.home() / ".reticulum"

    def _resolve_config_dir(self, preferred: str | Path | None) -> Path:
        target = (
            Path(preferred).expanduser() if preferred else self._default_config_root()
        )
        allow_fallback = preferred is None

        try:
            target.mkdir(parents=True, exist_ok=True)
        except Exception:
            if not allow_fallback:
                raise
            fallback = Path(tempfile.gettempdir()) / "ren_browser" / "reticulum"
            fallback.mkdir(parents=True, exist_ok=True)
            target = fallback

        self._seed_config_if_missing(target)
        return target

    def _default_tcp_interfaces_snippet(self) -> str:
        return """
  [[Quad4 Node 1]]
    type = TCPClientInterface
    interface_enabled = true
    target_host = rns.quad4.io
    target_port = 4242
    name = Quad4 Node 1
    selected_interface_mode = 1

  [[Quad4 Node 2]]
    type = TCPClientInterface
    interface_enabled = true
    target_host = rns2.quad4.io
    target_port = 4242
    name = Quad4 Node 2
    selected_interface_mode = 1
""".strip(
            "\n",
        )

    def _seed_config_if_missing(self, target: Path) -> None:
        config_file = target / "config"
        if config_file.exists():
            return

        base_content = None
        try:
            default_lines = getattr(RNS.Reticulum, "__default_rns_config__", None)
            if default_lines:
                if isinstance(default_lines, list):
                    base_content = "\n".join(default_lines)
                else:
                    base_content = str(default_lines)
        except Exception:
            base_content = None

        if not base_content:
            base_content = (
                "[reticulum]\n"
                "share_instance = Yes\n\n"
                "[interfaces]\n\n"
                "  [[Default Interface]]\n"
                "    type = AutoInterface\n"
                "    enabled = Yes\n"
            )

        snippet = self._default_tcp_interfaces_snippet()
        if snippet and snippet not in base_content:
            base_content = base_content.rstrip() + "\n\n" + snippet + "\n"

        try:
            config_file.write_text(base_content, encoding="utf-8")
            os.chmod(config_file, 0o600)
        except Exception:
            logger.exception("Failed to seed default config at %s", config_file)

    def _ensure_default_tcp_interfaces(self) -> None:
        if not self.config_path:
            return
        config_file = Path(self.config_path) / "config"
        if not config_file.exists():
            return

        try:
            content = config_file.read_text(encoding="utf-8")
        except Exception:
            return

        snippet = self._default_tcp_interfaces_snippet()
        if "target_host = rns.quad4.io" in content or "Quad4 Node 1" in content:
            return

        try:
            with open(config_file, "a", encoding="utf-8") as cfg:
                if not content.endswith("\n"):
                    cfg.write("\n")
                cfg.write("\n" + snippet + "\n")
        except Exception:
            logger.exception(
                "Failed to append default TCP interfaces to %s",
                config_file,
            )

    def _get_or_create_config_dir(self) -> Path:
        if self.config_path:
            return Path(self.config_path)

        resolved = self._resolve_config_dir(None)
        self.config_path = str(resolved)
        return resolved

    def initialize(self, config_dir: str | None = None) -> bool:
        """Initialize the Reticulum instance."""
        self.last_error = None
        try:
            use_custom_dir = bool(config_dir or self._is_android())
            if use_custom_dir:
                resolved = self._resolve_config_dir(config_dir)
                self.config_path = str(resolved)
                self.reticulum = RNS.Reticulum(configdir=self.config_path)
            else:
                self.reticulum = RNS.Reticulum()
                self.config_path = getattr(
                    RNS.Reticulum,
                    "configdir",
                    str(Path.home() / ".reticulum"),
                )

            self._ensure_default_tcp_interfaces()
            return True
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def shutdown(self) -> bool:
        """Shut down the active Reticulum instance."""
        try:
            if self.reticulum and hasattr(self.reticulum, "exit_handler"):
                self.reticulum.exit_handler()
        except Exception:
            return False
        finally:
            self.reticulum = None
        return True

    def read_config_file(self) -> str:
        """Return the current configuration file contents."""
        config_dir = self._get_or_create_config_dir()
        config_file = config_dir / "config"

        try:
            return config_file.read_text(encoding="utf-8")
        except FileNotFoundError:
            self._seed_config_if_missing(config_dir)
            try:
                return config_file.read_text(encoding="utf-8")
            except Exception:
                return ""
        except Exception:
            return ""

    def write_config_file(self, content: str) -> bool:
        """Persist configuration text to disk."""
        config_dir = self._get_or_create_config_dir()
        config_file = config_dir / "config"
        try:
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file.write_text(content, encoding="utf-8")
            os.chmod(config_file, 0o600)
            return True
        except Exception as exc:
            self.last_error = str(exc)
            return False

    def get_config_path(self) -> str | None:
        """Return the directory holding the active Reticulum config."""
        if self.config_path:
            return self.config_path
        try:
            default_path = self._resolve_config_dir(None)
            self.config_path = str(default_path)
            return self.config_path
        except Exception:
            return None

    def get_reticulum_instance(self):
        """Return the current Reticulum instance, if any."""
        return self.reticulum

    def get_last_error(self) -> str | None:
        """Return the last recorded error string."""
        return self.last_error


rns_manager = RNSManager()


def initialize_reticulum(config_dir: str | None = None) -> bool:
    """Initialize Reticulum using the shared manager."""
    return rns_manager.initialize(config_dir)


def shutdown_reticulum() -> bool:
    """Shut down the shared Reticulum instance."""
    return rns_manager.shutdown()


def get_reticulum_instance():
    """Expose the active Reticulum instance."""
    return rns_manager.get_reticulum_instance()


def get_config_path() -> str | None:
    """Expose the active configuration directory."""
    return rns_manager.get_config_path()


def read_config_file() -> str:
    """Read the Reticulum configuration file."""
    return rns_manager.read_config_file()


def write_config_file(content: str) -> bool:
    """Write the Reticulum configuration file."""
    return rns_manager.write_config_file(content)


def get_last_error() -> str | None:
    """Return the last recorded Reticulum error."""
    return rns_manager.get_last_error()
