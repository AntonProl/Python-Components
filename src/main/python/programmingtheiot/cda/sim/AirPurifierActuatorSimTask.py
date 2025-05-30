# AirPurifierActuatorSimTask.py
import logging
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask
from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData

_Logger = logging.getLogger(__name__)

class AirPurifierActuatorSimTask(BaseActuatorSimTask):
    def __init__(self):
        super(AirPurifierActuatorSimTask, self).__init__(
            actuatorName=ConfigConst.AIR_PURIFIER_ACTUATOR_NAME,
            actuatorType=ConfigConst.AIR_PURIFIER_ACTUATOR_TYPE,
            simpleName="PURIFIER") # Para feedback visual en emulador LED

    def _activateActuator(self, val: float = 0.0, state: str = None) -> int:
        msg = ""
        if self.latestActuatorData.getCommand() == ConfigConst.COMMAND_ON:
            self.latestActuatorData.setValue(1.0) # Representa encendido
            msg = f"ACTIVANDO {self.name}."
            if self.senseHAT: # Ejemplo de feedback visual
                self.senseHAT.show_message("AIR ON", scroll_speed = 0.05, text_colour = [0, 255, 0])
        elif self.latestActuatorData.getCommand() == ConfigConst.COMMAND_OFF:
            self.latestActuatorData.setValue(0.0) # Representa apagado
            msg = f"DESACTIVANDO {self.name}."
            if self.senseHAT:
                self.senseHAT.show_message("AIR OFF", scroll_speed = 0.05, text_colour = [255, 0, 0])
        else:
            _Logger.warning(f"Comando no soportado para {self.name}: {self.latestActuatorData.getCommand()}")
            return -1 # Error

        self.latestActuatorData.setStateData(msg)
        _Logger.info(f"Actuador {self.name}: {msg}")
        return 0 # Éxito