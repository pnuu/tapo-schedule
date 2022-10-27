"""Module for scheduling Tapo plugs and bulbs."""

import logging
import time

import yaml
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException

from tapo_schedule import Tapo

LOGGER = logging.getLogger(__name__)

MAX_RETRIES = 5
RETRY_SLEEP = 1


class Schedule:
    """Run schedule for Tapo devices."""

    def __init__(self, filename):
        """Initialize the schedule."""
        config = read_config(filename)
        self._password = config['password']
        self._user = config['user']
        self._ip = config['ip_address']
        self._schedule = config['schedule']
        self.device = None
        self._retry = 0
        self._initialize_device()

    def _initialize_device(self):
        self.device = Tapo(self._ip, self._user, self._password).get_device()

    def _run_command(self, method, value):
        try:
            if isinstance(value, list):
                method(*value)
            elif isinstance(value, int):
                method(value)
            else:
                method()
        except (KeyError, ConnectTimeout, ReadTimeout, RequestException):
            if self._retry < MAX_RETRIES:
                LOGGER.error("Connection problem, reconnecting")
                time.sleep(RETRY_SLEEP)
                self._initialize_device()
                self._retry += 1
                self._run_command(method, value, is_retry=True)
        self._retry = 0

    def run(self):
        """Process the schedule."""
        for itm in self._schedule:
            method = getattr(self.device, itm['method'])
            values = _get_values(itm)
            for value in values:
                start_time = time.time()
                self._run_command(method, value)
                end_time = time.time()
                delay = itm.get('delay', 0) - (end_time - start_time)
                if delay > 0:
                    LOGGER.debug(f"Sleeping {delay} seconds")
                    time.sleep(delay)
        LOGGER.info("Schedule completed")


def _get_values(itm):
    values = itm.get('values')
    if isinstance(values, dict):
        values = range(*values['range'])
    if values is None:
        values = [values]
    return values


def read_config(filename):
    """Read the configuration file."""
    with open(filename, 'r') as fid:
        config = yaml.load(fid, Loader=yaml.SafeLoader)
    return config
