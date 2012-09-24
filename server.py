from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
import rencode

import ConfigParser
from client							import Client
from game							import Game
from user 							import User

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

class Server(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)

		# Disable Mouse Control for camera
		self.disableMouse()
		
		camera.setPos(0,0,90)
		camera.lookAt(0,0,0)

		self.game = Game(True)

		# Server Networking handling stuff
		self.compress = False

		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager, 0)

		self.tempConnections = []
		self.unauthenticatedUsers = []
		self.users = []

		self.passedData = []

		self.connect(9099, 1000)
		self.startPolling()

	def connect(self, port, backlog = 1000):
		# Bind to our socket
		tcpSocket = self.cManager.openTCPServerRendezvous(port, backlog)
		self.cListener.addConnection(tcpSocket)

	def startPolling(self):
		taskMgr.add(self.tskListenerPolling, "serverListenTask", -40)
		taskMgr.add(self.tskDisconnectPolling, "serverDisconnectTask", -39)

	def tskListenerPolling(self, task):
		if self.cListener.newConnectionAvailable():
			rendezvous = PointerToConnection()
			netAddress = NetAddress()
			newConnection = PointerToConnection()

			if self.cListener.getNewConnection(rendezvous, netAddress, newConnection):
				newConnection = newConnection.p()
				newConnection.setNoDelay(True)
				self.tempConnections.append(newConnection) # Remember connection
				self.cReader.addConnection(newConnection)     # Begin reading connection
		return Task.cont

	def tskDisconnectPolling(self, task):
		while self.cManager.resetConnectionAvailable() == True:
			connPointer = PointerToConnection()
			self.cManager.getResetConnection(connPointer)
			connection = connPointer.p()
			
			# Remove the connection we just found to be "reset" or "disconnected"
			self.cReader.removeConnection(connection)
			
			# remove from our activeConnections list
			if connection in self.tempConnections:
				self.tempConnections.remove(connection)
			for user in self.unauthenticatedUsers:
				if connection == user.connection:
					self.unauthenticatedUsers.remove(user)
			for user in self.users:
				if connection == user.connection:
					user.connection = None
					self.passData(('disconnect', user.name), None)
		
		return Task.cont

	def broadcastData(self, data):
		# Broadcast data out to all users
		for user in self.users:
			self.sendData(data, user.connection)

	def processData(self, netDatagram):
		myIterator = PyDatagramIterator(netDatagram)
		return self.decode(myIterator.getString())

	def getUsers(self):
		# return a list of all users
		return self.users

	def encode(self, data, compress = False):
		# encode(and possibly compress) the data with rencode
		return rencode.dumps(data, compress)

	def decode(self, data):
		# decode(and possibly decompress) the data with rencode
		return rencode.loads(data)

	def sendData(self, data, con):
		myPyDatagram = PyDatagram()
		myPyDatagram.addString(self.encode(data, self.compress))
		self.cWriter.send(myPyDatagram, con)

	def passData(self, data, connection):
		self.passedData.append((data, connection))

	def getData(self):
		data = []
		for passed in self.passedData:
			data.append(passed)
			self.passedData.remove(passed)
		while self.cReader.dataAvailable():
			datagram = NetDatagram()
			if self.cReader.getData(datagram):
				if datagram.getConnection() in self.tempConnections:
					self.processTempConnection(datagram)
					continue
				for authed in self.users:
					if datagram.getConnection() == authed.connection:
						data.append((self.processData(datagram), datagram.getConnection()))
		return data

	def processTempConnection(self, datagram):
		connection = datagram.getConnection()
		package = self.processData(datagram)
		if len(package) == 2:
			if package[0] == 'username':
				print 'attempting to authenticate', package[1]
				self.tempConnections.remove(connection)
				if not self.online:
					self.users.append(User(package[1], connection))
				else:
					self.client.sendData(('auth',package[1]))
					self.unauthenticatedUsers.append(User(package[1], connection))

	def attempt_authentication(self):
		config = ConfigParser.RawConfigParser()
		config.read('server.cfg')
		self.SERVER_NAME = config.get('SERVER DETAILS', 'server_name')

		config = ConfigParser.RawConfigParser()
		config.read('master.cfg')
		self.LOGIN_IP = config.get('MASTER SERVER CONNECTION', 'master_ip')
		self.LOGIN_PORT = config.getint('MASTER SERVER CONNECTION', 'master_port')

		# Client for connecting to main server for showing exists and receiving clients
		self.client = Client(self.LOGIN_IP, self.LOGIN_PORT, compress = True)
		if self.client.getConnected():
			self.client.sendData(('server', self.SERVER_NAME))
			taskMgr.add(self.client_validator, 'Client Validator')
			self.client.sendData(('state', 'lobby'))
			self.online = True
		else:
			# client not connected to login/auth server
			print 'Could not connect to Authentication Server.'
			print 'Server is not in online mode. No Authentication will happen for clients.'
			print 'Restart Server to attempt to connect to Authentication Server.'
			self.client = None
			self.online = False

	def client_validator(self, task):
		temp = self.client.getData()
		if temp != []:
			for package in temp:
				if len(package) == 2:
					if package[0] == 'auth':
						print 'User authenticated: ', package[1]
						for user in self.unauthenticatedUsers:
							if user.name == package[1]:
								# send all required data to user
								# confirm authorization
								self.sendData(('auth', user.name), user.connection)
								# game data
								self.sendData(('game', self.game.packageData()), user.connection)
								for existing in self.users:
									self.sendData(('client', existing.name), user.connection)
									self.sendData(('ready', (existing.name, existing.ready)), user.connection)
									self.sendData(('client', user.name), existing.connection)
								self.sendData(('client', user.name), user.connection)
								# all authenticated users
								self.users.append(user)
								self.unauthenticatedUsers.remove(user)
								print 'confirmation sent to ', package[1]
								break
					elif package[0] == 'fail':
						print 'User failed authentication: ', package[1]
						for user in self.unauthenticatedUsers:
							if user.name == package[1]:
								self.sendData(('fail', user.name), user.connection)
								self.unauthenticatedUsers.remove(user)
								break
		return task.again
