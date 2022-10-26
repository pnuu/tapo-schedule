"""Package for scheduling and controlling TP-Link Tapo devices."""

import logging

from tapo_schedule._base import TapoCommunication
from tapo_schedule.l530 import L530
from tapo_schedule.p100 import P100
from tapo_schedule.p110 import P110

DEVICES = {
    'P100': P100,
    'P110': P110,
    'L510': L530,
    'L530': L530,
}
LOGGER = logging.getLogger()


class Tapo(TapoCommunication):
    """Utility class for creating device control objects."""

    def __init__(self, ip_address, email, password):
        """Initialize the class."""
        super().__init__(ip_address, email, password)

    def get_device(self):
        """Create device instance."""
        info = self.get_device_info()
        device = info['result']['model']
        LOGGER.info(f"{device} initialized.")
        return DEVICES[device](self.ip_address, self._email, self._password)
