"""Base module for TP-Link Tapo devices."""

import ast
import hashlib
import json
import logging
import time
import uuid
from base64 import b64decode, b64encode

from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from requests import Session

from tapo_schedule import tp_link_cipher
from tapo_schedule.utils import get_set_device_info_payload

COOKIE_NAME = "TP_SESSIONID"
RETRIES = 5
ERROR_CODES = {
    "0": "Success",
    "-1010": "Invalid Public Key Length",
    "-1012": "Invalid terminalUUID",
    "-1501": "Invalid Request or Credentials",
    "1002": "Incorrect Request",
    "-1003": "JSON formatting error",
    "-1008": "Invalid value",
}

LOGGER = logging.getLogger(__name__)


class TapoCommunication:
    """Base methods for communication with Tapo devices."""

    def __init__(self, ip_address, email, password):
        """Initialize the class."""
        self.ip_address = ip_address
        self._email = email
        self._password = password
        self._token = None
        self._tplink_cipher = None
        self._session = None
        self._app_url = f"http://{self.ip_address}/app"
        self._terminal_uuid = str(uuid.uuid4())
        self._headers = None
        self.connect()

    def _handshake(self):
        """Handle handshake with the device."""
        private_key, public_key = _create_key_pair()
        payload = _get_handshake_payload(public_key)
        response = self._get_response(self._app_url, payload)
        self._tplink_cipher = _decode_handshake_key(response.json()["result"]["key"], private_key)
        self._headers = _get_headers(response)

    def _login(self):
        """Handle login with the device."""
        email, password = _get_encrypted_credentials(self._email, self._password)
        payload = self._get_secure_payload(
            _get_login_payload(email, password)
        )
        response = self._get_decoded_response(self._app_url, payload)
        self._token = ast.literal_eval(response)["result"]["token"]
        self._log_response(response, "_login()")

    def connect(self):
        """Connect to the device."""
        self._session = Session()
        self._handshake()
        self._login()

    def close(self):
        """Close the current session."""
        if self._session:
            self._session.close()
        self._session = None

    def _get_decoded_response(self, url, payload):
        response = self._get_response(url, payload)
        return self._tplink_cipher.decrypt(response.json()["result"]["response"])

    def _get_response(self, url, payload):
        return self._session.post(url, json=payload, headers=self._headers, timeout=2)

    def _get_secure_payload(self, payload):
        return {
            "method": "securePassthrough",
            "params": {
                "request": self._tplink_cipher.encrypt(json.dumps(payload))
            }
        }

    def _log_response(self, response, cmd):
        if ast.literal_eval(response)["error_code"] != 0:
            error_code = ast.literal_eval(response)["error_code"]
            error_message = ERROR_CODES[str(error_code)]
            LOGGER.error(f"Command {cmd} failed with: {error_code}, {error_message}")
        else:
            LOGGER.debug(f"Command {cmd} succeeded.")

    def get_device_info(self):
        """Retrieve current settings from the device."""
        payload = self._get_secure_payload(
            _get_device_info_payload()
        )

        response = self._get_decoded_response(f"http://{self.ip_address}/app?token={self._token}", payload)

        return json.loads(response)


class TapoBase(TapoCommunication):
    """Base class for TP-Link Tapo devices."""

    def __init__(self, ip_address, email, password):
        """Initialize the class."""
        super().__init__(ip_address, email, password)

    def turn_on(self):
        """Power on the device."""
        payload = self._get_secure_payload(
            get_set_device_info_payload(self._terminal_uuid, params={"device_on": True})
        )
        response = self._get_decoded_response(f"http://{self.ip_address}/app?token={self._token}", payload)
        self._log_response(response, "turn_on()")

    def turn_off(self):
        """Power off the device."""
        payload = self._get_secure_payload(
            get_set_device_info_payload(self._terminal_uuid, params={"device_on": False})
        )
        response = self._get_decoded_response(f"http://{self.ip_address}/app?token={self._token}", payload)
        self._log_response(response, "turn_off()")

    def toggle_power(self):
        """Toggle device on/off."""
        if self.get_device_info()["result"]["device_on"]:
            self.turn_off()
        else:
            self.turn_on()

    def get_device_name(self):
        """Get the device name."""
        data = self.get_device_info()

        if data["error_code"] != 0:
            error_code = ast.literal_eval(data)["error_code"]
            error_message = ERROR_CODES[str(error_code)]
            raise Exception(f"Error Code: {error_code}, {error_message}")
        else:
            encoded_name = data["result"]["nickname"]
            name = b64decode(encoded_name)
            return name.decode("utf-8")

    def turn_on_with_delay(self, delay):
        """Switch on the device with a time delay."""
        payload = self._get_secure_payload(
            self._get_add_countdown_rule_payload(delay, True)
        )
        response = self._get_decoded_response(f"http://{self.ip_address}/app?token={self._token}", payload)
        self._log_response(response, "turn_on_with_delay()")

    def _get_add_countdown_rule_payload(self, delay, state):
        return {
            "method": "add_countdown_rule",
            "params": {
                "delay": int(delay),
                "desired_states": {
                    "on": state
                },
                "enable": True,
                "remain": int(delay)
            },
            "terminalUUID": self._terminal_uuid
        }

    def turn_off_with_delay(self, delay):
        """Switch off the device with a time delay."""
        payload = self._get_secure_payload(
            self._get_add_countdown_rule_payload(delay, False)
        )
        response = self._get_decoded_response(f"http://{self.ip_address}/app?token={self._token}", payload)
        self._log_response(response, "turn_off_with_delay()")


def _get_device_info_payload():
    return {
        "method": "get_device_info",
        "requestTimeMils": int(round(time.time() * 1000)),
    }


def _create_key_pair():
    """Create private and public keys."""
    keys = RSA.generate(1024)

    private_key = keys.exportKey("PEM")
    public_key = keys.public_key().exportKey("PEM")

    return private_key, public_key


def _decode_handshake_key(key, private_key):
    """Decode handshake."""
    decoded_key: bytes = b64decode(key.encode("UTF-8"))

    cipher = PKCS1_v1_5.new(RSA.importKey(private_key))
    decrypted_key = cipher.decrypt(decoded_key, None)
    if decrypted_key is None:
        raise ValueError("Decryption failed!")

    return tp_link_cipher.TpLinkCipher(decrypted_key[:16], decrypted_key[16:])


def _get_headers(response):
    try:
        return {
            "Cookie": f"{COOKIE_NAME}={response.cookies[COOKIE_NAME]}"
        }
    except Exception:
        error_code = response.json()["error_code"]
        error_message = ERROR_CODES[str(error_code)]
        raise Exception(f"Error Code: {error_code}, {error_message}")


def _get_handshake_payload(public_key):
    return {
        "method": "handshake",
        "params": {
            "key": public_key.decode("utf-8"),
            "requestTimeMils": int(round(time.time() * 1000))
        }
    }


def _get_encrypted_credentials(email, password):
    """Encrypt credentials."""
    password = b64encode(password.encode("utf-8")).decode("UTF-8")
    encoded_email = sha_digest(email)
    email = b64encode(encoded_email.encode("utf-8")).decode("UTF-8")

    return email, password


def _get_login_payload(email, password):
    return {
        "method": "login_device",
        "params": {
            "username": email,
            "password": password
        },
        "requestTimeMils": int(round(time.time() * 1000)),
    }


def sha_digest(data):
    """Digest string SHA."""
    b_arr = data.encode("UTF-8")
    digest = hashlib.sha1(b_arr).digest()

    sb = ""
    for i in range(0, len(digest)):
        b = digest[i]
        hex_string = hex(b & 255).replace("0x", "")
        if len(hex_string) == 1:
            sb += "0"
            sb += hex_string
        else:
            sb += hex_string

    return sb
