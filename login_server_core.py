from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
from db import ClientDataBase
import rencode

class Client:
	def __init__(self, name, connection):
		self.name = name
		self.connection = connection
		print 'Client connected: ', name, 'From: ', connection.getAddress()

class Server:
	def __init__(self, name, connection):
		self.name = name
		self.connection = connection
		self.state = 'starting'
		print 'Server connected: ', name, 'From: ', connection.getAddress()

class Chat:
	def __init__(self, name, connection):
		self.name = name
		self.private = False
		self.connection = connection
		print 'Chat Server connected: ', name, 'From: ', connection.getAddress()

# Login server Core.
class LoginServer:
	def __init__(self, port, backlog=1000, compress=False):
		self.compress = compress

		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		
		self.clientdb = ClientDataBase()
		if not self.clientdb.connected:
			self.clientdb = None
			self.alive = False
			return
		
		self.alive = True
		# This is for pre-login
		self.tempConnections = []
		
		# This is for authed clients
		self.active_clients = []
		# This is for authed servers
		self.active_servers = []
		# This is for authed chat servers
		self.active_chats = []
		
		self.connect(port, backlog)
		self.startPolling()

	def connect(self, port, backlog=1000):
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
				self.tempConnections.append(newConnection)
				self.cReader.addConnection(newConnection)
		return Task.cont

	def tskDisconnectPolling(self, task):
		while self.cManager.resetConnectionAvailable() == True:
			connPointer = PointerToConnection()
			self.cManager.getResetConnection(connPointer)
			connection = connPointer.p()
			
			# Remove the connection
			self.cReader.removeConnection(connection)
			# Check for if it was a client
			for client in self.active_clients:
				if client.connection == connection:
					self.active_clients.remove(client)
					break
			# then check servers
			for server in self.active_servers:
				if server.connection == connection:
					self.active_servers.remove(server)
					break
			# then check servers
			for chat in self.active_chats:
				if chat.connection == connection:
					self.active_chats.remove(chat)
					break
					
		return Task.cont

	def processData(self, netDatagram):
		myIterator = PyDatagramIterator(netDatagram)
		return self.decode(myIterator.getString())

	def encode(self, data, compress=False):
		# encode(and possibly compress) the data with rencode
		return rencode.dumps(data, compress)

	def decode(self, data):
		# decode(and possibly decompress) the data with rencode
		return rencode.loads(data)

	def sendData(self, data, con):
		myPyDatagram = PyDatagram()
		myPyDatagram.addString(self.encode(data, self.compress))
		self.cWriter.send(myPyDatagram, con)
		
	# This will check and do the logins.
	def auth(self, datagram): 
		# If in login state.
		con = datagram.getConnection()
		package = self.processData(datagram)
		if len(package) == 2:
			if package[0] == 'create':
				success, result = self.clientdb.add_client(package[1][0], package[1][1])
				if success:
					self.sendData(('create_success', result), con)
				else:
					self.sendData(('create_failed', result), con)
				return False
			if package[0] == 'client':
				user_found = False
				for client in self.active_clients:
					if client.name == package[1][0]:
						user_found = True
						self.sendData(('login_failed', 'logged'), con)
						break
				if not user_found:
					valid, result = self.clientdb.validate_client(package[1][0], package[1][1])
					if valid:
						self.active_clients.append(Client(package[1][0], con))
						self.sendData(('login_valid', result), con)
						return True
					else:
						self.sendData(('login_failed', result), con)
						return False
			# if server add it to the list of current active servers
			if package[0] == 'server':
				self.active_servers.append(Server(package[1], con))
				return True
			# if server add it to the list of current active servers
			if package[0] == 'chat':
				self.active_chats.append(Chat(package[1], con))
				return True

	def getData(self):
		data = []
		while self.cReader.dataAvailable():
			datagram = NetDatagram()
			if self.cReader.getData(datagram):
				if datagram.getConnection() in self.tempConnections:
					if self.auth(datagram):
						self.tempConnections.remove(datagram.getConnection())
						print "ACTIVE Clients: ", self.active_clients
						print "ACTIVE Servers: ", self.active_servers
						print "ACTIVE Chat Servers: ", self.active_chats
						print "TEMP Connections: ", self.tempConnections
					continue
				# Check if the data recieved is from a valid client.
				for client in self.active_clients:
					if datagram.getConnection() == client.connection:
						data.append(('client', self.processData(datagram), client))
						break
				# Check if the data recieved is from a valid server.
				for server in self.active_servers:
					if datagram.getConnection() == server.connection:
						data.append(('server', self.processData(datagram), server))
						break
				# Check if the data recieved is from a valid chat.
				for chat in self.active_chats:
					if datagram.getConnection() == chat.connection:
						data.append(('chat', self.processData(datagram), chat))
						break
		return data
