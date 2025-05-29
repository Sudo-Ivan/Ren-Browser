from typing import Optional, Dict
from pydantic import BaseModel
import os, time, threading
import RNS

class PageRequest(BaseModel):
    destination_hash: str
    page_path: str
    field_data: Optional[Dict] = None

class PageFetcher:
    """
    Fetcher to download pages from the Reticulum network.
    """
    def __init__(self):
        # Initialize Reticulum with default config (singleton)
        try:
            RNS.Reticulum()
        except OSError:
            # Already initialized
            pass

    def fetch_page(self, req: PageRequest) -> str:
        """
        Download page content for the given PageRequest.
        Placeholder implementation: replace with real network logic.
        """
        # Establish path and identity
        dest_bytes = bytes.fromhex(req.destination_hash)
        # Request path if needed, with timeout
        if not RNS.Transport.has_path(dest_bytes):
            RNS.Transport.request_path(dest_bytes)
            start = time.time()
            # Wait up to 30 seconds for path discovery
            while not RNS.Transport.has_path(dest_bytes):
                if time.time() - start > 30:
                    raise Exception(f"No path to destination {req.destination_hash}")
                time.sleep(0.1)
        # Recall identity
        identity = RNS.Identity.recall(dest_bytes)
        if not identity:
            raise Exception('Identity not found')
        # Create client destination and announce so the server learns our path
        destination = RNS.Destination(
            identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            'nomadnetwork',
            'node',
        )
        link = RNS.Link(destination)

        # Prepare sync fetch
        result = {'data': None}
        ev = threading.Event()

        def on_response(receipt):
            data = receipt.response
            if isinstance(data, bytes):
                result['data'] = data.decode('utf-8')
            else:
                result['data'] = str(data)
            ev.set()

        def on_failed(_):
            ev.set()

        # Set up request on link establishment
        link.set_link_established_callback(
            lambda l: l.request(req.page_path, req.field_data, response_callback=on_response, failed_callback=on_failed)
        )
        # Wait for response or timeout
        ev.wait(timeout=15)
        return result['data'] or 'No content received'
