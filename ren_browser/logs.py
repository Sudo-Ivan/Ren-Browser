import datetime
import RNS
APP_LOGS: list[str] = []
ERROR_LOGS: list[str] = []
RET_LOGS: list[str] = []
_original_RNS_log = RNS.log
def log_ret(msg, *args, **kwargs):
    timestamp = datetime.datetime.now().isoformat()
    RET_LOGS.append(f"[{timestamp}] {msg}")
    return _original_RNS_log(msg, *args, **kwargs)
RNS.log = log_ret

def log_error(msg: str):
    timestamp = datetime.datetime.now().isoformat()
    ERROR_LOGS.append(f"[{timestamp}] {msg}")
    APP_LOGS.append(f"[{timestamp}] ERROR: {msg}")

def log_app(msg: str):
    timestamp = datetime.datetime.now().isoformat()
    APP_LOGS.append(f"[{timestamp}] {msg}")
