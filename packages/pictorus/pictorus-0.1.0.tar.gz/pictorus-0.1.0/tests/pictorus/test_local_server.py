import json
from unittest import TestCase

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import jwt
from flask import Flask

from pictorus.constants import JWT_ALGORITHM, CmdType
from pictorus.date_utils import utc_timestamp_ms
from pictorus import local_server
from pictorus.local_server import app, COMMS, config, authenticated

KEY_PAIR = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = KEY_PAIR.public_key().public_bytes(
    encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
)
PRIVATE_KEY = KEY_PAIR.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)


class TestLocalServer(TestCase):
    def setUp(self):
        local_server.JWT_PUB_KEY = PUBLIC_KEY
        COMMS.clear()

    def test_timeseries(self):
        with app.test_client() as client:
            # Test unauthorized access
            response = client.get("/timeseries")
            assert response.status_code == 401

            token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}

            # Test empty data
            response = client.get("/timeseries", headers=headers)
            assert response.status_code == 200
            assert response.json == {"timeseries": {}}

            # Test with data
            utc_now = utc_timestamp_ms()
            ts0 = utc_now
            ts1 = utc_now + 1000
            ts2 = utc_now + 2000
            COMMS.update_telem({"test": 0, "utctime": ts0})
            COMMS.update_telem({"test": 1, "utctime": ts1})
            COMMS.update_telem({"test": 2, "utctime": ts2})
            response = client.get(f"/timeseries?start_time={ts0}", headers=headers)
            assert response.status_code == 200
            assert response.json == {"timeseries": {"test": [1, 2], "utctime": [ts1, ts2]}}

    def test_run_app_route(self):
        with app.test_client() as client:
            # Test unauthorized access
            response = client.post("/devices/123/run")
            assert response.status_code == 401

            # Test authorized access
            token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            response = client.post("/devices/123/run", headers=headers, json={"run_app": True})
            assert response.status_code == 200
            assert COMMS.commands.get() == (CmdType.RUN_APP, {"run_app": True})

    def test_get_device(self):
        with app.test_client() as client:
            # Test unauthorized access
            response = client.get("/devices/123")
            assert response.status_code == 401

            token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            # Test empty state
            response = client.get("/devices/123", headers=headers)
            assert response.status_code == 200
            assert response.json == {"id": "123", "reported_state": json.dumps({})}

            # Test populated state
            COMMS.reported_state = {"test": 1}
            response = client.get("/devices/123", headers=headers)
            assert response.status_code == 200
            assert response.json == {"id": "123", "reported_state": json.dumps({"test": 1})}

    def test_authenticated_decorator(self):
        test_app = Flask(__name__)

        @test_app.route("/test")
        @authenticated
        def test():
            return {}

        with test_app.test_client() as client:
            # Test missing authorization header
            response = client.get("/test")
            assert response.status_code == 401

            # Test invalid JWT token
            headers = {"Authorization": "Bearer invalid_token"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 401

            # Test missing sub key
            token = jwt.encode({}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 401

            # Test incorrect device ID
            token = jwt.encode({"sub": "invalid_device_id"}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 401

            # Test correct authorization
            token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/test", headers=headers)
            assert response.status_code == 200
