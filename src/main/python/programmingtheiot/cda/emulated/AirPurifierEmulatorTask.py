import logging
from programmingtheiot.cda.emulated.EmulatedTask import EmulatedTask
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData

class AirPurifierEmulatorTask(EmulatedTask):
    """
    Emulates an Air Purifier actuator.
    """

    def __init__(self):
        super(AirPurifierEmulatorTask, self).__init__(
            name = "AirPurifierEmulatorTask",
            actuatorType = ActuatorData.AIR_PURIFIER_ACTUATOR_TYPE,
            simpleName = "Air Purifier"
        )
        self.isOn = False

    def _handleActuatorData(self, data: ActuatorData) -> bool:
        """
        Handle incoming actuator data to emulate air purifier behavior.
        """
        if data is not None:
            if data.getCommand() == ActuatorData.COMMAND_ON:
                self.isOn = True
                logging.info("Air Purifier turned ON. Value: %s", data.getValue())
            elif data.getCommand() == ActuatorData.COMMAND_OFF:
                self.isOn = False
                logging.info("Air Purifier turned OFF.")
            else:
                logging.warning("Unknown command received: %s", data.getCommand())
            return True
        return False

    def getLatestActuatorResponse(self) -> ActuatorData:
        """
        Returns the latest actuator data response.
        """
        ad = ActuatorData(actuatorType=ActuatorData.AIR_PURIFIER_ACTUATOR_TYPE)
        ad.setCommand(ActuatorData.COMMAND_ON if self.isOn else ActuatorData.COMMAND_OFF)
        ad.setValue(1.0 if self.isOn else 0.0)
        return ad