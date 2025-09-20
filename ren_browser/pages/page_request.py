"""Page fetching functionality for Ren Browser.

Handles downloading pages from the Reticulum network using
the nomadnetwork protocol.
"""
import threading
import time
from dataclasses import dataclass

import RNS



@dataclass
class PageRequest:
    """Represents a request for a page from the Reticulum network.

    Contains the destination hash, page path, and optional field data.
    """

    destination_hash: str
    page_path: str
    field_data: dict | None = None

class PageFetcher:
    """Fetcher to download pages from the Reticulum network."""

    def __init__(self):
        """Initialize the page fetcher and Reticulum connection."""
        # RNS should already be initialized by main app

    @staticmethod
    def fetch_page(req: PageRequest) -> str:
        """Download page content for the given PageRequest.

        Args:
            req: PageRequest containing destination and path information.

        Returns:
            str: The downloaded page content.

        Raises:
            Exception: If no path to destination or identity not found.

        """
        RNS.log(f"PageFetcher: starting fetch of {req.page_path} from {req.destination_hash}")
        dest_bytes = bytes.fromhex(req.destination_hash)
        if not RNS.Transport.has_path(dest_bytes):
            RNS.Transport.request_path(dest_bytes)
            start = time.time()
            while not RNS.Transport.has_path(dest_bytes):
                if time.time() - start > 30:
                    raise Exception(f"No path to destination {req.destination_hash}")
                time.sleep(0.1)
        identity = RNS.Identity.recall(dest_bytes)
        if not identity:
            raise Exception("Identity not found")
        destination = RNS.Destination(
            identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            "nomadnetwork",
            "node",
        )
        link = RNS.Link(destination)

        result = {"data": None}
        ev = threading.Event()

        def on_response(receipt):
            data = receipt.response
            if isinstance(data, bytes):
                result["data"] = data.decode("utf-8")
            else:
                result["data"] = str(data)
            ev.set()

        def on_failed(_):
            ev.set()

        link.set_link_established_callback(
            lambda link: link.request(req.page_path, req.field_data, response_callback=on_response, failed_callback=on_failed)
        )
        ev.wait(timeout=15)
        data_str = result["data"] or "No content received"
        RNS.log(f"PageFetcher: received data for {req.destination_hash}:{req.page_path}")
        return data_str
