import logging
import unittest

from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.cda.sim.AirQualitySensorSimTask import AirQualitySensorSimTask

#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# Copyright (c) 2020 by Andrew D. King




class AirQualitySensorSimTaskTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    AirQualitySensorSimTask. It should not be considered complete,
    but serve as a starting point for the student implementing
    additional functionality within their Programming the IoT
    environment.
    """

    @classmethod
    def setUpClass(self):
        logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Testing AirQualitySensorSimTask class...")
        self.aqSimTask = AirQualitySensorSimTask()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    #@unittest.skip("Ignore for now.")
    def testGenerateTelemetry(self):
        sd = self.aqSimTask.generateTelemetry()

        self.assertIsNotNone(sd)

        # default simulator generates air quality values >= DEFAULT_VAL
        self.assertGreaterEqual(sd.getValue(), ConfigConst.DEFAULT_VAL)
        logging.info("Air Quality SensorData: %s", str(sd))

    #@unittest.skip("Ignore for now.")
    def testGetTelemetryValue(self):
        val = self.aqSimTask.getTelemetryValue()

        self.assertGreater(val, 0.0)
        logging.info("Air Quality data: %f", val)

if __name__ == "__main__":
    unittest.main()