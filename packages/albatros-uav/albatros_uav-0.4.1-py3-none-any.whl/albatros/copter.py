import logging

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_CMD_DO_SET_MODE,
    MAV_CMD_NAV_TAKEOFF,
)

from albatros.commands import get_command_long_message
from albatros.telemetry import ConnectionType

from .enums import CopterFlightModes, MavCommandResult
from .uav import UAV

logger = logging.getLogger(__name__)


class Copter(UAV):
    """Class that provides actions the copter can perform."""

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
        super().__init__(
            vehicle_system_id,
            vehicle_component_id,
            my_sys_id,
            my_cmp_id,
            connection_type,
            device,
            baud_rate,
            host,
        )

    def set_mode(self, mode: CopterFlightModes) -> bool:
        """Set system mode.

        :param mode: ardupilot flight mode you want to set.
        """
        msg = get_command_long_message(
            target_system=self.target_system,
            target_component=self.target_component,
            command=MAV_CMD_DO_SET_MODE,
            param1=1,
            param2=mode.value,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Set mode command sent")

        if self.get_command_ack().result != MavCommandResult.ACCEPTED:
            return False
        return True

    def takeoff(self, alt_m: float, yaw: float = float("NaN")) -> bool:
        """Takeoff copter. Set Guided mode and send takeoff command.

        :param alt_m: The altitude to which the Copter is to ascend
        :param yaw: Yaw angle (if magnetometer present), ignored without magnetometer.
            NaN to use the current system yaw heading mode (e.g. yaw towards next waypoint,
            yaw to home, etc.).
        """
        if not self.set_mode(CopterFlightModes.GUIDED):
            logger.error("Unable to set GUIDED mode, aborting")
            return False

        msg = get_command_long_message(
            self.target_system,
            self.target_component,
            MAV_CMD_NAV_TAKEOFF,
            param4=yaw,
            param7=alt_m,
        )

        self.telem.send(msg.pack(self.mav))
        logger.info("Takeoff command sent")

        if self.get_command_ack().result != MavCommandResult.ACCEPTED:
            return False
        return True
