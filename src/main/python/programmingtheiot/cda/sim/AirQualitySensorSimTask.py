# AirQualitySensorSimTask.py
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.data.SensorData import SensorData
import random

class AirQualitySensorSimTask(BaseSensorSimTask):
    def __init__(self, dataSet=None):
        super(AirQualitySensorSimTask, self).__init__(
            name=ConfigConst.AIR_QUALITY_SENSOR_NAME,
            typeID=ConfigConst.AIR_QUALITY_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=50.0,
            maxVal=300.0
        )
        
        # Initialize latest sensor data
        self.latestSensorData = SensorData(typeID=self.typeID, name=self.name)
        self.latestSensorData.setValue(ConfigConst.DEFAULT_VAL)
        
        # Dataset handling
        self.dataSet = dataSet
        if self.dataSet:
            self.useRandomizer = False
            self.dataSetIndex = 0
        else:
            self.useRandomizer = True

    def generateTelemetry(self):
        """
        Generates a new telemetry data point.
        If using a dataset, retrieves the next value from the dataset.
        Otherwise, generates a random value within the specified range.
        """
        if self.useRandomizer:
            value = random.uniform(self.minVal, self.maxVal)
        else:
            value = self.dataSet.getDataEntry(index=self.dataSetIndex)
            self.dataSetIndex += 1
            if self.dataSetIndex >= self.dataSet.getDataEntryCount():
                self.dataSetIndex = 0

        self.latestSensorData.setValue(value)
        return self.latestSensorData

    def getTelemetryValue(self):
        """
        Returns the latest telemetry value. If no value is present, it generates one.
        """
        if self.latestSensorData:
            return self.latestSensorData.getValue()
        else:
            return self.generateTelemetry().getValue()