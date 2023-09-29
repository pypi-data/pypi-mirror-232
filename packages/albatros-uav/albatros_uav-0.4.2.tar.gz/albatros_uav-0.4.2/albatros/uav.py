"""
A module that provides high-level functions to perform actions on UAVs.
"""
import logging
import time

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_CMD_COMPONENT_ARM_DISARM,
    MAV_CMD_DO_REPOSITION,
    MAV_CMD_DO_SET_SERVO,
    MAV_MODE_FLAG_SAFETY_ARMED,
    MAVLink,
)

from .commands import get_command_int_message, get_command_long_message
from .enums import MavCommandResult
from .message_models import CommandACK
from .nav.position import PositionGPS, PositionNED, ned2geo
from .telemetry import ConnectionType, Telemetry

logger = logging.getLogger(__name__)


class UAV:
    """Class that provides actions that the UAV can perform.
    Actions are common for aircraft and copter vehicle type.
    """

    def __init__(
        self,
        vehicle_system_id: int = 1,
        vehicle_component_id: int = 1,
        my_sys_id: int = 1,
        my_cmp_id: int = 191,
        connection_type: ConnectionType = ConnectionType.DIRECT,
        device: str = "udpin:0.0.0.0:14550",
        baud_rate: int = 115200,
        host: str = "localhost",
    ) -> None:
        self.target_system = vehicle_system_id
        self.target_component = vehicle_component_id
        self.mav = MAVLink(0, my_sys_id, my_cmp_id)
        self.telem = Telemetry(connection_type, device, baud_rate, host)

    def wait_gps_fix(self) -> None:
        """Wait for GPS 3D fix."""
        while (
            self.telem.data.gps_raw_int.fix_type < 3
            or self.telem.data.gps_raw_int.lat == 0
        ):
            time.sleep(0.1)

    def is_armed(self) -> bool:
        """Check whether the UAV is armed."""
        armed_flag = self.telem.data.heartbeat.base_mode & MAV_MODE_FLAG_SAFETY_ARMED
        return bool(armed_flag)

    def wait_heartbeat(self) -> None:
        """Wait for next heartbeat message."""
        while time.time() * 1000 - self.telem.data.heartbeat.timestamp_ms > 100:
            time.sleep(0.1)
        time.sleep(0.1)

    def arm(self) -> bool:
        """Arms motors."""
        msg = get_command_long_message(
            target_system=self.target_system,
            target_component=self.target_component,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=1,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Arm command sent.")
        self.wait_heartbeat()

        return self.is_armed()

    def disarm(self) -> bool:
        """Disarms motors."""
        msg = get_command_long_message(
            target_system=self.target_system,
            target_component=self.target_component,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=0,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Disarm command sent.")

        if self.get_command_ack().result != MavCommandResult.ACCEPTED:
            return False
        return True

    def set_servo(self, instance_number: int, pwm: int) -> bool:
        """Set a servo to a desired PWM value.

        :param instance_number: servo number.
        :param pwm: PWM value to set.
        """
        msg = get_command_long_message(
            target_system=self.target_system,
            target_component=self.target_component,
            command=MAV_CMD_DO_SET_SERVO,
            param1=instance_number,
            param2=pwm,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Set servo command sent.")

        if self.get_command_ack().result != MavCommandResult.ACCEPTED:
            return False
        return True

    def fly_to_gps_position(self, lat_int: int, lon_int: int, alt_m: float) -> bool:
        """Reposition the vehicle to a specific WGS84 global position.

        :param lat_int: Latitude of the target point.
        :param lon_int: Longitude of the target point.
        :param alt_m: Altitude of the target point in meters.

        Works only in Guided mode.
        """
        msg = get_command_int_message(
            target_system=self.target_system,
            target_component=self.target_component,
            command=MAV_CMD_DO_REPOSITION,
            x=lat_int,
            y=lon_int,
            z=alt_m,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Flight to point command sent.")

        if self.get_command_ack().result != MavCommandResult.ACCEPTED:
            return False
        return True

    def get_command_ack(self) -> CommandACK:
        """Get command execution status.

        :returns: CommandACK object containing a execution result.
        """
        clock_start = time.time()
        while True:
            time_dif = time.time() * 1000 - self.telem.data.command_ack.timestamp_ms
            if time_dif < 100:
                self.telem.data.command_ack.timestamp_ms = 0
                return self.telem.data.command_ack
            time.sleep(0.1)
            if time.time() - clock_start > 0.250:
                raise TimeoutError

    def get_corrected_position(self) -> PositionGPS:
        """
        :returns: the vehicle position corrected for the distance the vehicle traveled after the message was received.
        """
        movement_time = (
            time.time() - self.telem.data.global_position_int.timestamp_ms / 1000
        )
        north_shift = movement_time * self.telem.data.global_position_int.vx / 100
        east_shift = movement_time * self.telem.data.global_position_int.vy / 100
        z_shift = movement_time * self.telem.data.global_position_int.vz / 100
        corrected_altitude = (
            z_shift + self.telem.data.global_position_int.relative_alt / 1000
        )
        last_known_position = PositionGPS(
            self.telem.data.global_position_int.lat,
            self.telem.data.global_position_int.lon,
        )
        shift_vector = PositionNED(north_shift, east_shift, corrected_altitude)
        return ned2geo(last_known_position, shift_vector)
