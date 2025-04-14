import logging
import unittest

from time import sleep

from programmingtheiot.common.ConfigConst import ConfigConst

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
        logging.info("Ejecutando la clase MqttClientControlPacketTest...")

        self.cfg = ConfigUtil()

        # NOTA: Asegúrate de usar un clientID DIFERENTE al que se utiliza
        # para tu CDA cuando se ejecute por separado de esta prueba
        #
        # El clientID mostrado abajo es solo un ejemplo; por favor usa tu propio
        # valor único para esta prueba
        self.mcc = MqttClientConnector(clientID = "MqttClient_test1")

    def setUp(self):
        try:
            self.assertTrue(self.mcc.connectClient(), "La conexión al servidor MQTT falló.")
        except Exception as e:
            logging.error(f"Error al conectar el cliente MQTT: {e}")
            raise

    def tearDown(self):
        try:
            if not self.mcc.disconnectClient():
                logging.warning("El cliente MQTT ya está desconectado.")
        except Exception as e:
            logging.error(f"Error al desconectar el cliente MQTT: {e}")
            raise

    def testConnectAndDisconnect(self):
        logging.info("Probando conexión y desconexión...")
        self.assertTrue(self.mcc.connectClient(), "La conexión al servidor MQTT falló.")
        sleep(2)
        self.assertTrue(self.mcc.disconnectClient(), "La desconexión del servidor MQTT falló.")

    def testServerPing(self):
        logging.info("Probando ping al servidor...")
        self.assertTrue(self.mcc.connectClient(), "La conexión al servidor MQTT falló.")
        sleep(2)
        self.assertTrue(self.mcc.sendPing(), "El ping al servidor MQTT falló.")
        self.assertTrue(self.mcc.disconnectClient(), "La desconexión del servidor MQTT falló.")

    def testPubSub(self):
        # TODO: implement this test
		#
		# IMPORTANT: be sure to use QoS 1 and 2 to see ALL control packets
        testTopic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value
        testMessage = "Test message for Pub/Sub"
        qosLevel = 1

        # Define a callback to capture the received message
        def onMessageReceived(topic, message):
            logging.info(f"Mensaje recibido en el topic '{topic}': {message}")
            self.assertEqual(testMessage, message, "El mensaje recibido no coincide con el mensaje publicado.")

        # Set the callback for incoming messages
        listener = DefaultDataMessageListener()
        listener.onMessageReceived = onMessageReceived
        self.mcc.setDataMessageListener(listener)

        # Connect the client
        self.assertTrue(self.mcc.connectClient(), "La conexión al servidor MQTT falló.")
        sleep(2)

        # Subscribe to the topic
        self.assertTrue(self.mcc.subscribeToTopic(testTopic, qosLevel), "La suscripción al topic falló.")
        sleep(2)

        # Publish a message to the topic
        self.assertTrue(self.mcc.publishMessage(testTopic, testMessage, qosLevel), "La publicación del mensaje falló.")
        sleep(2)

        # Disconnect the client
        self.assertTrue(self.mcc.disconnectClient(), "La desconexión del servidor MQTT falló.")