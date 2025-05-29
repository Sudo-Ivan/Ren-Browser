import threading
import time
import pathlib

import RNS
from dataclasses import dataclass


@dataclass
class PageRequest:
    destination_hash: str
    page_path: str
    field_data: dict | None = None

class PageFetcher:
    """
    Fetcher to download pages from the Reticulum network.
    """

    def __init__(self):
        config_dir = pathlib.Path(__file__).resolve().parents[2] / "config"
        try:
            RNS.Reticulum(str(config_dir))
        except (OSError, ValueError):
            pass

    def fetch_page(self, req: PageRequest) -> str:
        RNS.log(f"PageFetcher: starting fetch of {req.page_path} from {req.destination_hash}")
        """
        Download page content for the given PageRequest.
        Placeholder implementation: replace with real network logic.
        """
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
            raise Exception('Identity not found')
        destination = RNS.Destination(
            identity,
            RNS.Destination.OUT,
            RNS.Destination.SINGLE,
            'nomadnetwork',
            'node',
        )
        link = RNS.Link(destination)

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

        link.set_link_established_callback(
            lambda l: l.request(req.page_path, req.field_data, response_callback=on_response, failed_callback=on_failed)
        )
        ev.wait(timeout=15)
        data_str = result['data'] or 'No content received'
        RNS.log(f"PageFetcher: received data for {req.destination_hash}:{req.page_path}")
        return data_str
