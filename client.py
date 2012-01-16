#!/usr/bin/env python

from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
import rencode

class Client:
	def __init__(self, host, port, timeout=3000, compress=False):
		self.host = host
		self.port = port
		self.timeout = timeout
		self.compress = compress

		self.cManager = QueuedConnectionManager()
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)

		# By default, we are not connected
		self.connected = False

		self.connect(self.host, self.port, self.timeout)
		self.startPolling()

	def connect(self, host, port, timeout=3000):
		# Connect to our host's socket
		self.myConnection = self.cManager.openTCPClientConnection(host, port, timeout)
		if self.myConnection:
			self.cReader.addConnection(self.myConnection)  # receive messages from server
			self.connected = True # Let us know that we're connected

	def startPolling(self):
		taskMgr.add(self.tskDisconnectPolling, "clientDisconnectTask", -39)

	def tskDisconnectPolling(self, task):
		while self.cManager.resetConnectionAvailable() == True:
			connPointer = PointerToConnection()
			self.cManager.getResetConnection(connPointer)
			connection = connPointer.p()

			# Remove the connection we just found to be "reset" or "disconnected"
			self.cReader.removeConnection(connection)

			# Let us know that we are not connected
			self.connected = False

		return Task.cont

	def processData(self, netDatagram):
		myIterator = PyDatagramIterator(netDatagram)
		return self.decode(myIterator.getString())

	def getConnected(self):
		# Check whether we are connected or not
		return self.connected

	def encode(self, data, compress=False):
		# encode(and possibly compress) the data with rencode
		return rencode.dumps(data, compress)

	def decode(self, data):
		# decode(and possibly decompress) the data with rencode
		return rencode.loads(data)

	def sendData(self, data):
		myPyDatagram = PyDatagram()
		myPyDatagram.addString(self.encode(data, self.compress))
		self.cWriter.send(myPyDatagram, self.myConnection)

	def getData(self):
		data = []
		while self.cReader.dataAvailable():
			datagram = NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
			if self.cReader.getData(datagram):
				data.append(self.processData(datagram))
		return data

	def appendData(self,data):
		while self.cReader.dataAvailable():
			datagram = NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
			if self.cReader.getData(datagram):
				data.append(self.processData(datagram))
		return data
