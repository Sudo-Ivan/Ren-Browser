import os, time, base64, asyncio, json, logging
import RNS
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from LXMF import LXMRouter, LXMessage
from queue import Queue
from pydantic import BaseModel
from typing import Optional, List, Dict
import threading
from types import SimpleNamespace
import argparse
import msgpack


# Setup logging
def setup_logging(debug=False):
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = "%(asctime)s - %(levelname)s - %(message)s"

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(log_format))

    # File handler
    file_handler = logging.FileHandler("debug.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(log_format))

    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


class MessageRequest(BaseModel):
    destination: str
    message: str
    title: Optional[str] = "Reply"


class PageRequest(BaseModel):
    destination_hash: str
    page_path: str
    field_data: Optional[Dict] = None


class Node(BaseModel):
    hash: str
    name: str
    last_seen: int


class Announce(BaseModel):
    destination_hash: str
    identity_hash: str
    display_name: Optional[str]
    aspect: str
    created_at: int
    updated_at: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LXMFHandler:
    receipts = []
    queue = Queue(maxsize=5)
    announce_time = 0
    nodes = {}
    nodes_file = "nodes.json"
    announces = {}
    cached_links = {}

    def __init__(self, name="RenBrowser"):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing LXMFHandler")

        # Setup Reticulum and LXMF
        self.config_path = os.path.join(os.getcwd(), "config")
        if not os.path.isdir(self.config_path):
            os.mkdir(self.config_path)

        idfile = os.path.join(self.config_path, "identity")
        if not os.path.isfile(idfile):
            RNS.log("No Primary Identity file found, creating new...", RNS.LOG_INFO)
            id = RNS.Identity(True)
            id.to_file(idfile)
        self.id = RNS.Identity.from_file(idfile)

        RNS.Reticulum(loglevel=RNS.LOG_VERBOSE)
        self.router = LXMRouter(identity=self.id, storagepath=self.config_path)
        self.local = self.router.register_delivery_identity(self.id, display_name=name)

        # Register announce handler
        RNS.Transport.register_announce_handler(self._handle_announces)

        RNS.log(
            "LXMF Router ready to receive on: {}".format(
                RNS.prettyhexrep(self.local.hash)
            ),
            RNS.LOG_INFO,
        )

        self._start_queue_processor()
        self._start_node_cleanup()

        # Disable announces
        self.announce_time = 0
        self.last_announce = 0

        # Load saved nodes on startup
        self.load_nodes()

    def _handle_announces(self, announce):
        """Single handler for all announces"""
        try:
            # Convert bytes to hex string for storage
            dest_hash = announce.destination_hash.hex()
            self.announces[dest_hash] = announce

            if announce.aspect == "lxmf.delivery":
                self._on_lxmf_announce(announce)
            elif announce.aspect == "lxmf.propagation":
                self._on_propagation_announce(announce)

            self.logger.debug(f"Stored announce from {dest_hash}")
        except Exception as e:
            self.logger.error(f"Error handling announce: {str(e)}")

    def _on_lxmf_announce(self, announce):
        self.logger.debug(
            f"Received LXMF announce from {RNS.prettyhexrep(announce.destination_hash)}"
        )
        display_name = None
        if announce.app_data:
            try:
                display_name = announce.app_data.decode("utf-8")
            except:
                pass

        # Save node when we receive an announce
        self.update_node(announce.destination_hash.hex(), display_name or "Unknown")

    def _on_propagation_announce(self, announce):
        self.logger.debug(
            f"Received propagation announce from {RNS.prettyhexrep(announce.destination_hash)}"
        )

    async def get_announces(self, aspect: Optional[str] = None) -> List[Announce]:
        announces = []
        try:
            for dest_hash, announce in self.announces.items():
                if aspect and announce.aspect != aspect:
                    continue
                announces.append(
                    Announce(
                        destination_hash=dest_hash,  # Already hex string
                        identity_hash=announce.identity.hash.hex(),
                        display_name=(
                            announce.app_data.decode("utf-8")
                            if announce.app_data
                            else None
                        ),
                        aspect=announce.aspect,
                        created_at=int(announce.timestamp),
                        updated_at=int(announce.timestamp),
                    )
                )
        except Exception as e:
            self.logger.error(f"Error getting announces: {str(e)}")
        return announces

    def load_nodes(self):
        """Load nodes from JSON file"""
        if os.path.exists(self.nodes_file):
            try:
                with open(self.nodes_file, "r") as f:
                    self.nodes = json.load(f)
                self.logger.info(
                    f"Loaded {len(self.nodes)} nodes from {self.nodes_file}"
                )
            except Exception as e:
                self.logger.error(f"Error loading nodes: {str(e)}")
                self.nodes = {}

    def save_nodes(self):
        """Save nodes to JSON file"""
        try:
            with open(self.nodes_file, "w") as f:
                json.dump(self.nodes, f, indent=2)
            self.logger.debug(f"Saved {len(self.nodes)} nodes to {self.nodes_file}")
        except Exception as e:
            self.logger.error(f"Error saving nodes: {str(e)}")

    def update_node(self, hash: str, name: str):
        """Update node and save to file"""
        self.nodes[hash] = {"hash": hash, "name": name, "last_seen": int(time.time())}
        self.save_nodes()

    def _start_node_cleanup(self):
        def cleanup():
            while True:
                current_time = int(time.time())
                self.nodes = {
                    k: v
                    for k, v in self.nodes.items()
                    if current_time - v["last_seen"] < 86400
                }
                self.save_nodes()
                time.sleep(3600)

        thread = threading.Thread(target=cleanup, daemon=True)
        thread.start()

    def _start_announce_handler(self):
        def announce():
            while True:
                if self.announce_time > 0:
                    current_time = time.time()
                    if current_time - self.last_announce >= self.announce_time:
                        self.local.announce()
                        self.last_announce = current_time
                time.sleep(60)

        thread = threading.Thread(target=announce, daemon=True)
        thread.start()

    def _message_received(self, message):
        try:
            sender = RNS.hexrep(message.source_hash, delimit=False)
            receipt = RNS.hexrep(message.hash, delimit=False)
            RNS.log(f"Message receipt <{receipt}>", RNS.LOG_INFO)

            # Update node's last seen time
            source_name = getattr(message, "source_name", "Unknown")
            self.update_node(sender, source_name)

            if receipt not in self.receipts:
                self.receipts.append(receipt)
                if len(self.receipts) > 100:
                    self.receipts.pop(0)
        except Exception as e:
            RNS.log(f"Error processing message: {str(e)}", RNS.LOG_ERROR)

    def _start_queue_processor(self):
        def process_queue():
            while True:
                if not self.queue.empty():
                    lxm = self.queue.get()
                    self.router.handle_outbound(lxm)
                time.sleep(10)

        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()

    def send(self, destination: str, message: str, title="Reply"):
        try:
            hash = bytes.fromhex(destination)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid destination hash")

        if not len(hash) == RNS.Reticulum.TRUNCATED_HASHLENGTH // 8:
            raise HTTPException(
                status_code=400, detail="Invalid destination hash length"
            )

        id = RNS.Identity.recall(hash)
        if id is None:
            RNS.Transport.request_path(hash)
            raise HTTPException(
                status_code=404, detail="Identity not found, path requested"
            )

        lxmf_destination = RNS.Destination(
            id, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery"
        )
        lxm = LXMessage(
            lxmf_destination,
            self.local,
            message,
            title=title,
            desired_method=LXMessage.DIRECT,
        )
        lxm.try_propagation_on_fail = True
        self.queue.put(lxm)
        return {"status": "queued", "destination": destination}

    def convert_nomadnet_string_data_to_map(self, path_data: str | None):
        data = {}
        if path_data is not None:
            for field in path_data.split("|"):
                if "=" in field:
                    variable_name, variable_value = field.split("=")
                    data[f"var_{variable_name}"] = variable_value
        return data

    def convert_nomadnet_field_data_to_map(self, field_data):
        data = {}
        if field_data is not None:
            try:
                if isinstance(field_data, dict):
                    data = {f"field_{key}": value for key, value in field_data.items()}
            except Exception as e:
                self.logger.error(f"Error converting field data: {e}")
        return data

    async def download_page(
        self, destination_hash: str, page_path: str, field_data: Optional[Dict] = None
    ) -> Dict:
        try:
            dest_hash_bytes = bytes.fromhex(destination_hash)

            # Create destination with correct app name and aspects
            identity = RNS.Identity.recall(dest_hash_bytes)
            if not identity:
                raise HTTPException(status_code=404, detail="Identity not found")

            destination = RNS.Destination(
                identity,
                RNS.Destination.OUT,
                RNS.Destination.SINGLE,
                "nomadnetwork",  # Changed from lxmf
                "node",  # Added aspect
            )

            # Use existing link or create new one
            link = None
            if dest_hash_bytes in self.cached_links:
                link = self.cached_links[dest_hash_bytes]
                if link.status != RNS.Link.ACTIVE:
                    link = None

            if not link:
                link = RNS.Link(destination)
                timeout = time.time() + 15
                while link.status != RNS.Link.ACTIVE and time.time() < timeout:
                    await asyncio.sleep(0.1)

                if link.status != RNS.Link.ACTIVE:
                    raise HTTPException(
                        status_code=504, detail="Could not establish link"
                    )

                self.cached_links[dest_hash_bytes] = link

            # Prepare request data
            request_data = {"request": "page", "path": page_path}
            if field_data:
                request_data["data"] = field_data

            # Create Future for response
            response_future = asyncio.Future()

            def on_response(request_receipt):
                if hasattr(request_receipt, "response") and request_receipt.response:
                    response_future.set_result(request_receipt.response)
                else:
                    response_future.set_exception(
                        Exception("No response data received")
                    )

            def on_failed(_):
                if not response_future.done():
                    response_future.set_exception(Exception("Request failed"))

            # Request over link with callbacks
            link.request(
                page_path,
                data=field_data,
                response_callback=on_response,
                failed_callback=on_failed,
                timeout=15,
            )

            try:
                response = await asyncio.wait_for(response_future, timeout=15)
                return {
                    "content": (
                        response.decode("utf-8") if response else "No content received"
                    )
                }
            except asyncio.TimeoutError:
                raise HTTPException(status_code=504, detail="Page request timed out")

        except Exception as e:
            self.logger.error(f"Error downloading page: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def cleanup_links(self):
        """Remove inactive links from cache"""
        self.cached_links = {
            hash: link
            for hash, link in self.cached_links.items()
            if link.status == RNS.Link.ACTIVE
        }

    async def shutdown(self):
        """Clean shutdown of Reticulum"""
        # Close all cached links
        for link in self.cached_links.values():
            link.close()
        self.cached_links.clear()

        try:
            RNS.Transport.detach_interfaces()
            RNS.exit()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")

    async def establish_link(
        self,
        destination_hash: bytes,
        path_lookup_timeout: int = 15,
        link_establishment_timeout: int = 15,
    ) -> RNS.Link:
        # Check existing cached link
        if destination_hash in self.cached_links:
            link = self.cached_links[destination_hash]
            if link.status == RNS.Link.ACTIVE:
                self.logger.debug("Using existing active link")
                return link

        # Wait for path
        timeout = time.time() + path_lookup_timeout
        if not RNS.Transport.has_path(destination_hash):
            RNS.Transport.request_path(destination_hash)
            while (
                not RNS.Transport.has_path(destination_hash) and time.time() < timeout
            ):
                await asyncio.sleep(0.1)

        if not RNS.Transport.has_path(destination_hash):
            raise HTTPException(
                status_code=404, detail="Could not find path to destination"
            )

        # Establish link
        identity = RNS.Identity.recall(destination_hash)
        destination = RNS.Destination(
            identity, RNS.Destination.OUT, RNS.Destination.SINGLE, "lxmf", "delivery"
        )

        link = RNS.Link(destination)
        timeout = time.time() + link_establishment_timeout

        while link.status != RNS.Link.ACTIVE and time.time() < timeout:
            await asyncio.sleep(0.1)

        if link.status != RNS.Link.ACTIVE:
            raise HTTPException(status_code=504, detail="Could not establish link")

        self.cached_links[destination_hash] = link
        return link


lxmf_instance = None


@app.on_event("startup")
async def startup_event():
    global lxmf_instance
    lxmf_instance = LXMFHandler()


# Create v1 router
v1_router = APIRouter(prefix="/api/v1")


# Move routes to v1
@v1_router.get("/")
async def root():
    return {"status": "running", "address": RNS.prettyhexrep(lxmf_instance.local.hash)}


@v1_router.get("/nodes")
async def get_nodes():
    """Get all LXMF announces and saved nodes"""
    announces = await lxmf_instance.get_announces("lxmf.delivery")

    saved_nodes = []
    for node_hash, node in lxmf_instance.nodes.items():
        saved_nodes.append(
            Announce(
                destination_hash=node["hash"],
                identity_hash="",
                display_name=node["name"],
                aspect="lxmf.delivery",
                created_at=node["last_seen"],
                updated_at=node["last_seen"],
            )
        )

    seen = set()
    combined = []
    for node in announces + saved_nodes:
        if node.destination_hash not in seen:
            seen.add(node.destination_hash)
            combined.append(node)

    return combined


@v1_router.get("/status")
async def get_status():
    return {
        "status": "Connected",
        "address": RNS.prettyhexrep(lxmf_instance.local.hash),
        "queue_size": lxmf_instance.queue.qsize(),
        "receipts_count": len(lxmf_instance.receipts),
        "nodes_count": len(lxmf_instance.nodes),
    }


@v1_router.post("/send")
async def send_message(message_request: MessageRequest):
    return lxmf_instance.send(
        message_request.destination, message_request.message, message_request.title
    )


@v1_router.post("/page")
async def get_page(page_request: PageRequest):
    try:
        response = await lxmf_instance.download_page(
            page_request.destination_hash,
            page_request.page_path,
            page_request.field_data,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Include router in app
app.include_router(v1_router)


# Update FastAPI app shutdown handler
@app.on_event("shutdown")
async def shutdown_event():
    await lxmf_instance.shutdown()


def main():
    parser = argparse.ArgumentParser(description="LXMF API Server")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    args = parser.parse_args()

    logger = setup_logging(args.debug)

    if args.debug:
        logger.debug("Debug logging enabled")

    # Start the FastAPI application
    import uvicorn

    uvicorn.run(
        app, host=args.host, port=args.port, log_level="debug" if args.debug else "info"
    )


if __name__ == "__main__":
    main()