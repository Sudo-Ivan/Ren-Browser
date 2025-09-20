"""Reticulum network announce handling for Ren Browser.

This module provides services for listening to and collecting network
announces from the Reticulum network.
"""
import time
from dataclasses import dataclass

import RNS

from ren_browser.storage.storage import get_rns_config_directory


@dataclass
class Announce:
    """Represents a Reticulum network announce.

    Contains destination hash, display name, and timestamp.
    """

    destination_hash: str
    display_name: str | None
    timestamp: int

class AnnounceService:
    """Service to listen for Reticulum announces and collect them.

    Calls update_callback whenever a new announce is received.
    """

    def __init__(self, update_callback):
        """Initialize the announce service.

        Args:
            update_callback: Function called when new announces are received.

        """
        self.aspect_filter = "nomadnetwork.node"
        self.receive_path_responses = True
        self.announces: list[Announce] = []
        self.update_callback = update_callback
        config_dir = get_rns_config_directory()
        try:
            RNS.Reticulum(str(config_dir))
            from ren_browser.logs import setup_rns_logging
            setup_rns_logging()
        except (OSError, ValueError):
            pass
        RNS.Transport.register_announce_handler(self)
        RNS.log("AnnounceService: registered announce handler")

    def received_announce(self, destination_hash, announced_identity, app_data):
        """Handle received announce from Reticulum network.

        Args:
            destination_hash: Hash of the announcing destination.
            announced_identity: Identity of the announcer.
            app_data: Optional application data from the announce.

        """
        RNS.log(f"AnnounceService: received announce from {destination_hash.hex()}")
        ts = int(time.time())
        display_name = None
        if app_data:
            try:
                display_name = app_data.decode("utf-8")
            except UnicodeDecodeError:
                pass
        announce = Announce(destination_hash.hex(), display_name, ts)
        self.announces = [ann for ann in self.announces if ann.destination_hash != announce.destination_hash]
        self.announces.insert(0, announce)
        if self.update_callback:
            self.update_callback(self.announces)

    def get_announces(self) -> list[Announce]:
        """Return collected announces."""
        return self.announces
