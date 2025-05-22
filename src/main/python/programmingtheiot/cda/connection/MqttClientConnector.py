#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import paho.mqtt.client as mqttClient

from programmingtheiot.common.ConfigConst import ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient
from programmingtheiot.data.DataUtil import DataUtil

import ssl

class MqttClientConnector(IPubSubClient):
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self, clientID: str = None):
		"""
		Default constructor. This will set remote broker information and client connection
		information based on the default configuration file contents.
		
		@param clientID Defaults to None. Can be set by caller. If this is used, it's
		critically important that a unique, non-conflicting name be used so to avoid
		causing the MQTT broker to disconnect any client using the same name. With
		auto-reconnect enabled, this can cause a race condition where each client with
		the same clientID continuously attempts to re-connect, causing the broker to
		disconnect the previous instance.
		"""
		self.config = ConfigUtil()
		self.dataMsgListener = None

		self.host = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)

		self.port = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)

		self.keepAlive = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)

		self.defaultQos = \
			self.config.getInteger( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)

		self.mqttClient = None

		# Configuración de TLS/SSL
		self.enableEncryption = \
			self.config.getBoolean( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.ENABLE_CRYPT_KEY)

		self.pemFileName = \
			self.config.getProperty( \
				ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.CERT_FILE_KEY)
		
		self.dataMsgListener = None



	# IMPORTANTE:
	#
	# Puedes elegir establecer clientID de varias maneras:
	#  1 - usar el valor locationID en PiotConfig.props como el clientID (ver abajo)
	#  2 - pasar un clientID personalizado al constructor (desde DeviceDataManager o tu prueba)
	#  3 - codificar un clientID directamente en este constructor (generalmente no recomendado)
	#  4 - si usas Python Paho, no configures un clientID y permite que el broker asigne automáticamente un valor aleatorio (no recomendado si configuras la bandera de sesión limpia como False)

		# Si no se proporciona un clientID, intenta obtenerlo de la configuración
		if not clientID:
			self.clientID = self.config.getProperty(
				ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY
		 )
			# Si no se encuentra en la configuración, usa un ID predeterminado
			if not self.clientID:
				self.clientID = "DefaultClientID"
		else:
			self.clientID = clientID
		
		

		# Validar el clientID para asegurarse de que no esté vacío
		if not self.clientID or len(self.clientID.strip()) == 0:
			raise ValueError("El clientID no puede estar vacío. Proporcione un ID válido.")

		logging.info('\tMQTT Client ID:   ' + self.clientID)
		logging.info('\tMQTT Broker Host: ' + self.host)
		logging.info('\tMQTT Broker Port: ' + str(self.port))
		logging.info('\tMQTT Keep Alive:  ' + str(self.keepAlive))

	
		
	def connectClient(self) -> bool:
		if self.mqttClient and not self.mqttClient.is_connected():  # Si existe pero no está conectado
			try:
				logging.debug("Intentando detener loop anterior antes de reconectar...")
				self.mqttClient.loop_stop(force=True)  # force=True puede ser necesario
				logging.debug("Loop anterior detenido.")
			except Exception as e:
				logging.warning(f"Error al detener loop anterior: {e}")
			# Considerar hacer self.mqttClient = None aquí para forzar la recreación completa abajo
			# self.mqttClient = None 

		if not self.mqttClient:  # O si lo hiciste None arriba
			self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=True)
			# Configurar TLS si está habilitado
			if self.enableEncryption:
				try:
					logging.info("Habilitando cifrado TLS...")
					self.port = self.config.getInteger(
						ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.SECURE_PORT_KEY, ConfigConst.DEFAULT_MQTT_SECURE_PORT)
					self.mqttClient.tls_set(self.pemFileName, tls_version=ssl.PROTOCOL_TLS_CLIENT)
				except Exception as e:
					logging.warning(f"Fallo al habilitar el cifrado TLS: {e}. Usando conexión no cifrada.")

			self.mqttClient.on_connect = self.onConnect
			self.mqttClient.on_disconnect = self.onDisconnect
			self.mqttClient.on_message = self.onMessage
			self.mqttClient.on_publish = self.onPublish
			self.mqttClient.on_subscribe = self.onSubscribe

		if not self.mqttClient.is_connected():
			try:
				logging.info(f'MQTT client connecting to broker at host: {self.host}:{self.port}')
				self.mqttClient.connect(self.host, self.port, self.keepAlive)
				self.mqttClient.loop_start()

				# Sincronización CRÍTICA para tests: esperar a que on_connect se dispare.
				# Para una solución más robusta, usa threading.Event.
				import time
				# Espera un momento para que el callback on_connect se ejecute
				# y las suscripciones se procesen.
				# Aumenta si los tests siguen siendo inestables.
				time.sleep(1.5)  # ANTES era 1 segundo, probemos un poco más

				# Devuelve el estado real DESPUÉS de dar tiempo a conectar
				if self.mqttClient.is_connected():
					logging.info("Conexión exitosa verificada después de la espera.")
					return True
				else:
					logging.warning("La conexión falló después de la espera o on_connect no se completó/falló.")
					# Si falló la conexión (ej. rc != 0 en on_connect), loop_start podría seguir corriendo.
					# Es buena idea detenerlo si la conexión no es exitosa.
					try:
						self.mqttClient.loop_stop(force=True)
					except Exception as e:
						logging.error(f"Error stopping MQTT loop: {e}")
					return False
			except Exception as e:
				logging.error(f"Excepción durante el intento de conexión: {e}")
				# Asegurar que si hay error, el loop se detiene si llegó a iniciarse
				try:
					if self.mqttClient: 
						self.mqttClient.loop_stop(force=True)
				except:
					pass
				return False
		else:
			logging.warning('MQTT client is already connected. Ignoring connect request.')
			return True  # Si ya está conectado, la "solicitud de conexión" es exitosa en cierto modo

	def disconnectClient(self) -> bool:
		if self.mqttClient.is_connected():
			logging.info('Disconnecting MQTT client from broker: ' + self.host)
			self.mqttClient.loop_stop()
			self.mqttClient = None
			self.mqttClient.disconnect()

			return True
		elif self.mqttClient: # Existe pero no está conectado
			logging.warning('MQTT client exists but is not connected. Attempting to stop loop if running.')
			try:
				self.mqttClient.loop_stop(force=True)
			except Exception as e:
				logging.error(f"Error stopping MQTT loop: {e}")
			return False  # Indica que no estaba conectado para desconectar

		else:
			logging.warning('MQTT client already disconnected. Ignoring.')

			return False
		
	def onConnect(self, client, userdata, flags, rc):
		logging.info('MQTT client connected to broker: ' + str(client))

		# Subscribe to the topic
		self.mqttClient.subscribe( \
			topic=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value, qos=self.defaultQos)

		self.mqttClient.message_callback_add( \
			sub = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE.value, \
			callback = self.onActuatorCommandMessage)
		
	def onDisconnect(self, client, userdata, rc):
		logging.info('MQTT client disconnected from broker: ' + str(client))
		
	def onMessage(self, client, userdata, msg):
		payload = msg.payload

		if payload:
			logging.info('MQTT message received with payload: ' + str(payload.decode("utf-8")))
		else:
			logging.info('MQTT message received with no payload: ' + str(msg))
			
	def onPublish(self, client, userdata, mid):
		logging.info('MQTT message published: ' + str(client))
	
	def onSubscribe(self, client, userdata, mid, granted_qos):
		logging.info('MQTT client subscribed: ' + str(client))
	
	def onActuatorCommandMessage(self, client, userdata, msg):
		"""
		This callback is defined as a convenience, but does not
		need to be used and can be ignored.
		
		It's simply an example for how you can create your own
		custom callback for incoming messages from a specific
		topic subscription (such as for actuator commands).
		
		@param client The client reference context.
		@param userdata The user reference context.
		@param msg The message context, including the embedded payload.
		"""
		logging.info('[Callback] Mensaje de comando del actuador recibido. Tópico: %s.', msg.topic)

		if self.dataMsgListener:
			try:
				# asume que todos los datos están codificados usando UTF-8 (entre GDA y CDA)
				actuatorData = DataUtil().jsonToActuatorData(msg.payload.decode('utf-8'))

				self.dataMsgListener.handleActuatorCommandMessage(actuatorData)
			except:
				logging.exception("Fallo al convertir el payload del comando de actuación entrante a ActuatorData: ")

	def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		# verificar validez del recurso (tema)
		if not resource:
			logging.warning('No se especificó un tema. No se puede publicar el mensaje.')
			return False

		# verificar validez del mensaje
		if not msg:
			logging.warning('No se especificó un mensaje. No se puede publicar el mensaje en el tema: ' + resource)
			return False

		# verificar validez de QoS - establecer a predeterminado si es necesario
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		# Convertir el recurso a cadena si es un enum
		topic = resource.value if isinstance(resource, ResourceNameEnum) else str(resource)

		# publicar mensaje y esperar a que se complete la publicación antes de regresar
		msgInfo = self.mqttClient.publish(topic = topic, payload = msg, qos = qos)
		msgInfo.wait_for_publish()

		return True

	def setDataMessageListener(self, listener: IDataMessageListener = None):
		if listener:
			self.dataMsgListener = listener

	""""
	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		# verificar validez del recurso (tema)
		if not resource:
			logging.warning('No se especificó un tema. No se puede suscribir.')
			return False
		

		# verificar validez de QoS - establecer a predeterminado si es necesario
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		
		# suscribirse al tema
		logging.info('Suscribiéndose al tema %s', resource)
		self.mqttClient.subscribe(resource, qos)

		return True
"""
	
	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback=None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
    	# Verificar validez del recurso (tema)
		if not resource:
			logging.warning('No se especificó un tema. No se puede suscribir.')
			return False

		# Convertir el recurso a cadena si es un enum
		topic = resource.value if isinstance(resource, ResourceNameEnum) else str(resource)

		# Verificar validez de QoS - establecer a predeterminado si es necesario
		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS
			
		try:
			logging.info(f'Suscribiéndose al tema: {topic}')
			self.mqttClient.subscribe(topic, qos)
			return True
		except Exception as e:
			logging.error(f'Error al suscribirse al tema {topic}: {e}')
			return False

	def unsubscribeFromTopic(self, resource: ResourceNameEnum = None):
		# verificar validez del recurso (tema)
		if not resource:
			logging.warning('No se especificó un tema. No se puede cancelar la suscripción.')
			return False

		logging.info('Cancelando suscripción al tema %s', resource)
		self.mqttClient.unsubscribe(resource)

		return True


	def setDataMessageListener(self, listener: IDataMessageListener = None):
		if listener:
			self.dataMsgListener = listener

	def sendPing(self) -> bool:
        # Implement the sendPing method
		try:
			# Logic to send a ping to the MQTT broker
			return True
		except Exception as e:
			logging.error(f"Error sending ping: {e}")
			return False
