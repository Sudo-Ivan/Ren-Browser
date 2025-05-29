import RNS
import time
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Announce:
    destination_hash: str
    display_name: Optional[str]
    timestamp: int

class AnnounceService:
    """
    Service to listen for Reticulum announces and collect them.
    Calls update_callback whenever a new announce is received.
    """
    def __init__(self, update_callback):
        # Accept all announce aspects
        self.aspect_filter = "nomadnetwork.node"
        self.receive_path_responses = True
        self.announces: List[Announce] = []
        self.update_callback = update_callback
        # Initialize Reticulum transport once
        try:
            RNS.Reticulum()
        except OSError:
            # Already initialized
            pass
        # Register self as announce handler
        RNS.Transport.register_announce_handler(self)

    def received_announce(self, destination_hash, announced_identity, app_data):
        # Called by RNS when an announce is received
        ts = int(time.time())
        display_name = None
        if app_data:
            try:
                display_name = app_data.decode("utf-8")
            except:
                pass
        announce = Announce(destination_hash.hex(), display_name, ts)
        # Deduplicate and move announce to top
        # Remove any existing announces with same destination_hash
        self.announces = [ann for ann in self.announces if ann.destination_hash != announce.destination_hash]
        # Insert new announce at front of list
        self.announces.insert(0, announce)
        # Notify UI of new announce
        if self.update_callback:
            self.update_callback(self.announces)

    def get_announces(self) -> List[Announce]:
        """Return collected announces."""
        return self.announces
