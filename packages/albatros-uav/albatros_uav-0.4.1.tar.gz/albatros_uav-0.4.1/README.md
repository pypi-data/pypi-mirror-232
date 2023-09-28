# Albatros UAV

A python library that provides high-level functions for UAVs based on MAVLink. It allows to easily handle communication with the flight controller to create friendly mission management systems. Albatross supports direct communication with UAVs as well as via Redis (WIP)

### Supported functionalities

*Plane:*

- arming vehicle,
- setting flight mode,
- setting servos positions,
- flying in `GUIDED` mode,
- uploading mission and flying in `AUTO` mode.

*Copter:*

- arming vehicle,
- setting flight mode,
- setting servos positions,
- flying in `GUIDED` mode,
- __comming soon:__ uploading mission and flying in `AUTO` mode.

### Supported MAVLink telemetry messages

- `Attitude`
- `GlobalPositionInt`
- `GPSRawInt`
- `GPSStatus`
- `Heartbeat`
- `CommandACK`
- `MissionACK`
- `MissionRequestInt`
- `RadioStatus`
- `RcChannelsRaw`
- `ServoOutputRaw`
- `SysStatus`
- `MissionItemReached`

## Examples

### Creating connection
```python
from albatros.plane import Plane
from albatros.telemetry import ConnectionType

# SITL connection is default
plane = Plane() 

# Direct connection to the flight controller
plane = Plane(device="/dev/tty/USB0/", baud_rate=57600)

# You can also specify the ID of the vehicle you want to connect to and the ID of your system
# read more about MAVLink Routing in ArduPilot: https://ardupilot.org/dev/docs/mavlink-routing-in-ardupilot.html
plane = Plane(vehicle_system_id=1, vehicle_component_id=1, my_sys_id=1, my_cmp_id=191)
```

### Arming vehicle (in SITL simulation)

Simply arm and disarm vehicle

Flow:
arm vehicle
wait for the vehicle to be armed
disarm vehicle

```bash
$ python -m examples.arming_vehicle
```

```python
from albatros.copter import Copter

copter = Copter()

while not copter.arm():
    print("waiting ARM")

copter.disarm()
```
