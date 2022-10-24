# Tapo Schedule
Tapo Schedule is a Python library for controlling TP-Link Tapo P100/P105/P110 plugs and L530/L510E bulbs
and scheduling their operation.

The device control portion of the package is a rewrite of [PyP100](https://github.com/fishbigger/TapoP100) library.

> **_NOTE:_**  The library is still a work in progress. The device controls work, but the scheduling is still missing

## Installation

> **_NOTE:__**  The package will be available in PyPI in due time

```bash
pip install https://github.com/pnuu/tapo-schedule.git
```

## Usage

### Schedules
Todo

### Device initialization.
Any supported device can be initialized using the ``Tapo`` utility class.

```python
from tapo_schedule import Tapo

device = Tapo("192.168.X.X", "email@gmail.com", "Password123").get_device()
```

### Plugs - P100, P105 etc.

The plug devices have the following methods. Initialize the device as shown above.

```python
# Power on the device
device.turn_on()
# Power off the device
device.turn_off()
# Get a dictionary of device information
device.get_device_info()
```

### Bulbs - L510E, L530 etc.

In addition to the commands for the plugs above, additional commands are available for light bulbs.
Initialize the device as shown above.

```python
# Set brightness level
device.set_brightness(100)
# Set color temperature for the white light (2700 K, warm white)
device.set_color_temp(2700)
# Set hue, saturation and value (HSV colorspace) for L530E
device.set_hsv(240, 100, 100)  # Blue
# Set RGB colors
device.set_rgb(255, 0, 255)  # Purple
```

### Energy Monitoring plug - P110

In addition to P100 plugs, the following command is available for P110 power monitoring plug.
Initialize the device as shown above.

```python
# Returns a dict with all the energy usage statistics
device.get_energy_usage()
```
