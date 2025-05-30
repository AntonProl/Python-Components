import logging
from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from pisense import SenseHAT
import random

class AirQualitySensorEmulatorTask(BaseSensorSimTask):
    """
    Emulated Air Quality Sensor using SenseHAT (simulated AQI values).
    """

    def __init__(self):
        super(AirQualitySensorEmulatorTask, self).__init__(
            name=ConfigConst.AIR_QUALITY_SENSOR_NAME,
            typeID=ConfigConst.AIR_QUALITY_SENSOR_TYPE,
        )

        enableEmulation = ConfigUtil().getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY
        )

        self.sh = SenseHAT(emulate=enableEmulation)
        self._curValue = 0.0

    def _getTelemetryValue(self) -> float:
        # Simula un valor AQI entre 0 y 500
        self._curValue = random.uniform(0, 500)
        return self._curValue

    def displayValue(self):
        if self.sh.screen:
            msg = f"AQI: {int(self._curValue)}"
            self.sh.screen.scroll_text(msg)
        else:
            logging.warning("No SenseHAT LED screen instance to write AQI value.")