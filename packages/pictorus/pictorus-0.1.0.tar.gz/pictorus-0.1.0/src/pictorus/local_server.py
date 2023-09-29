import logging
from collections import defaultdict, deque
from queue import Queue
from typing import Dict, Deque, Tuple
from functools import wraps
import json

from flask import Flask, request
from flask_cors import CORS
import jwt

from .config import Config
from .constants import CmdType, JWT_ALGORITHM, JWT_PUB_KEY
from .date_utils import utc_timestamp_ms

# Disable default flask logging
logging.getLogger("werkzeug").disabled = True
config = Config()

app = Flask(__name__)
CORS(app)

MAX_RECENT_TELEM_SAMPLES = int(10000)
MAX_TIMESERIES_AGE_S = 300

LocalDbType = Dict[str, Deque[Tuple[float, float]]]


class ThreadComms:
    def __init__(self):
        self._data: LocalDbType = defaultdict(lambda: deque(maxlen=MAX_RECENT_TELEM_SAMPLES))
        self.reported_state = None
        self.commands = Queue()

    def add_command(self, cmd_type: CmdType, cmd_data: dict):
        self.commands.put((cmd_type, cmd_data))

    def update_telem(self, sample: dict):
        for key, val in sample.items():
            if isinstance(val, str):
                try:
                    json_val = json.loads(val)
                    if isinstance(json_val, list):
                        val = json_val
                except json.JSONDecodeError:
                    pass

            self._data[key].append(val)

    def get_telem(self, requested_start_time: int, max_age_s: int) -> Dict:
        timestamp_data = self._data.get("utctime")
        if not timestamp_data:
            start_index = 0
        else:
            utc_now = utc_timestamp_ms()
            start_time = max(utc_now - max_age_s * 1000, requested_start_time)
            start_index = next(
                (i for i, ts in enumerate(timestamp_data) if ts > start_time),
                0,
            )

        return {key: list(vals)[start_index:] for key, vals in self._data.items()}

    def clear(self):
        self._data.clear()
        self.reported_state = None
        self.commands = Queue()


COMMS = ThreadComms()


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" not in request.headers:
            return {"error": "Missing authorization header"}, 401

        try:
            token = request.headers["Authorization"].split(" ")[1]
            decoded = jwt.decode(token, JWT_PUB_KEY, algorithms=[JWT_ALGORITHM])
        except Exception as e:
            return {"error": "Invalid JWT token"}, 401

        if "sub" not in decoded:
            return {"error": "Missing sub key"}, 401

        device_id = decoded["sub"]
        if device_id != config.client_id:
            return {"error": "Incorrect device ID"}, 401

        return func(*args, **kwargs)

    return wrapper


@app.route("/timeseries", methods=["GET"])
@authenticated
def timeseries():
    start_time = float(request.args.get("start_time", 0))
    requested_age_s = int(request.args.get("age_s", MAX_TIMESERIES_AGE_S))
    max_age_s = min(requested_age_s, MAX_TIMESERIES_AGE_S)
    return {"timeseries": COMMS.get_telem(start_time, max_age_s)}


@app.route("/devices/<device_id>/run", methods=["POST"])
@authenticated
def run_app_route(device_id: str):
    request_data = request.get_json()
    if "run_app" not in request_data:
        return {"error": "Missing run_app key"}, 400

    COMMS.add_command(CmdType.RUN_APP, {"run_app": request_data["run_app"]})
    return {}


@app.route("/devices/<device_id>", methods=["GET"])
@authenticated
def get_device(device_id: str):
    return {"id": device_id, "reported_state": json.dumps(COMMS.reported_state or {})}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5151, debug=True)
