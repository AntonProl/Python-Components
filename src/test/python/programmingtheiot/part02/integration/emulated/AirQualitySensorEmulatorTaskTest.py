import logging
import unittest
from time import sleep
from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.emulated.AirQualitySensorEmulatorTask import AirQualitySensorEmulatorTask

#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# Copyright (c) 2020 by Andrew D. King
#





class AirQualitySensorEmulatorTaskTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    AirQualitySensorEmulatorTask. It should not be considered complete,
    but serve as a starting point for the student implementing
    additional functionality within their Programming the IoT
    environment.

    NOTE: This test requires the sense_emu_gui to be running
    and must have access to the underlying libraries that
    support the pisense module. On Windows, one way to do
    this is by installing pisense and sense-emu within the
    Bash on Ubuntu on Windows environment and then execute this
    test case from the command line, as it will likely fail
    if run within an IDE in native Windows.
    """

    @classmethod
    def setUpClass(self):
        logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
        logging.info("Testing AirQualitySensorEmulatorTask class [using SenseHAT emulator]...")
        self.aqSimTask = AirQualitySensorEmulatorTask()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGenerateTelemetry(self):
        # Simulate reading air quality data multiple times
        for i in range(3):
            sd = self.aqSimTask.generateTelemetry()
            self.assertIsNotNone(sd)
            self.assertIsInstance(sd, SensorData)
            self.assertEqual(sd.getTypeID(), ConfigConst.AIR_QUALITY_SENSOR_TYPE)
            logging.info("SensorData: " + str(sd))
            sleep(2)

if __name__ == "__main__":
    unittest.main()