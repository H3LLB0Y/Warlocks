#!/usr/bin/env python

from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
import rencode

class Server:
	def __init__(self, port, backlog=1000, compress=False):
		self.port = port
		self.backlog = backlog
		self.compress = compress

		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)

		self.activeConnections = [] # We'll want to keep track of these later

		self.connect(self.port, self.backlog)
		self.startPolling()

	def connect(self, port, backlog=1000):
		# Bind to our socket
		tcpSocket = self.cManager.openTCPServerRendezvous(port, backlog)
		tcpSocket.setNoDelay(True)
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
				self.activeConnections.append(newConnection) # Remember connection
				self.cReader.addConnection(newConnection)     # Begin reading connection
		return Task.cont

	def tskDisconnectPolling(self, task):
		while self.cManager.resetConnectionAvailable() == True:
			print "disconnect"
			connPointer = PointerToConnection()
			self.cManager.getResetConnection(connPointer)
			connection = connPointer.p()
			
			# Remove the connection we just found to be "reset" or "disconnected"
			self.cReader.removeConnection(connection)
			
			# Loop through the activeConnections till we find the connection we just deleted
			# and remove it from our activeConnections list
			for c in range(0, len(self.activeConnections)):
				if self.activeConnections[c] == connection:
					del self.activeConnections[c]
					break
					
		return Task.cont

	def broadcastData(self, data):
		# Broadcast data out to all activeConnections
		for con in self.activeConnections:
			self.sendData(data, con)

	def processData(self, netDatagram):
		myIterator = PyDatagramIterator(netDatagram)
		return self.decode(myIterator.getString())

	def getClients(self):
		# return a list of all activeConnections
		return self.activeConnections

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

	def getData(self):
		data = []
		while self.cReader.dataAvailable():
			datagram = NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
			if self.cReader.getData(datagram):
				appendage={}
				appendage[0]=self.processData(datagram)
				appendage[1]=datagram.getConnection()
				data.append(appendage)
		return data
