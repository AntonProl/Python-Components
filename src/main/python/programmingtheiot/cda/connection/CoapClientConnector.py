#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import socket

from programmingtheiot.common.ConfigConst import ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient
from programmingtheiot.data.DataUtil import DataUtil

from coapthon import defines
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri
from coapthon.utils import generate_random_token
import traceback

class CoapClientConnector(IRequestResponseClient):
	"""
	Shell representation of class for student implementation.
	
	"""
	
	def __init__(self, dataMsgListener: IDataMessageListener = None):
		self.config = ConfigUtil()
		self.dataMsgListener = dataMsgListener
		self.enableConfirmedMsgs = False
		self.coapClient = None

		self.observeRequests = {}

		self.host = self.config.getProperty(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.HOST_KEY,
			ConfigConst.DEFAULT_HOST
		)
		self.port = self.config.getInteger(
			ConfigConst.COAP_GATEWAY_SERVICE,
			ConfigConst.PORT_KEY,
			ConfigConst.DEFAULT_COAP_PORT
		)
		self.uriPath = "coap://" + self.host + ":" + str(self.port) + "/"

		logging.info('\tHost:Port: %s:%s', self.host, str(self.port))

		self.includeDebugLogDetail = True

		try:
			tmpHost = socket.gethostbyname(self.host)

			if tmpHost:
				self.host = tmpHost
				self._initClient()
			else:
				logging.error("No se puede resolver el host: " + self.host)

		except socket.gaierror:
			logging.info("No se pudo resolver el host: " + self.host)
	
	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		pass

	def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		logging.info("Discovering remote resources...")
		
		return self.sendGetRequest(
        	resource=None,
        	name='.well-known/core',
        	enableCON=False,
        	timeout=timeout
    )


	def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		pass

	def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		if resource or name:
			resourcePath = self._createResourcePath(resource, name)
			
			logging.info("Issuing GET with path: " + resourcePath)

			request = self.coapClient.mk_request(defines.Codes.GET, path=resourcePath)
			request.token = generate_random_token(2)
	
			if not enableCON:
				request.type = defines.Types["NON"]
	
			response = self.coapClient.send_request(request=request, timeout=timeout)
	
			self._onGetResponse(response=response, resourcePath=resourcePath)
		else:
			logging.warning("Can't test GET - no path or path list provided.")

	def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		pass

	def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None, enableCON: bool = False, payload: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		pass

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		pass

	def startObserver(self, resource: ResourceNameEnum = None, name: str = None, ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
		asyncio.get_event_loop().run_until_complete(self._handleStartObserveRequest(resourceName))


	def stopObserver(self, resource: ResourceNameEnum = None, name: str = None, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
		pass
	
	def _initClient(self):
		try:
			self.coapClient = HelperClient(server=(self.host, self.port))
			logging.info('Cliente creado. Invocará recursos en: ' + self.uriPath)
		except Exception as e:
			# evidentemente, esto es un fallo crítico - es posible que desees manejar esto de manera diferente
			logging.error("No se pudo crear el cliente CoAP para la ruta URI: " + self.uriPath)
			traceback.print_exception(type(e), e, e.__traceback__)

	def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None):
		resourcePath = ""
		hasResource = False

		if resource:
			resourcePath = resourcePath + resource.value
			hasResource = True

		if name:
			if hasResource:
				resourcePath = resourcePath + '/'

			resourcePath = resourcePath + name

		return resourcePath

	def _onGetResponse(self, response, resourcePath: str = None):
		if not response:
			logging.warning('GET response invalid. Ignoring.')
			return

		logging.info('GET response received.')

		jsonData = response.payload
		locationPath = resourcePath.split('/') if resourcePath else []

		if len(locationPath) > 2:
			dataType = locationPath[2]

			if dataType == ConfigConst.ACTUATOR_CMD:
				try:
					ad = DataUtil().jsonToActuatorData(jsonData)

					if self.dataMsgLiSstener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except Exception as e:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					logging.error("Exception: %s", str(e))

				try:
					ad = DataUtil().jsonToActuatorData(jsonData)

					if self.dataMsgListener:
						self.dataMsgListener.handleActuatorCommandMessage(ad)
				except:
					logging.warning("Failed to decode actuator data. Ignoring: %s", jsonData)
					return
		else:
			logging.info("Response data received. Payload: %s", jsonData)
			logging.info("Response data received. Payload: %s", jsonData)

