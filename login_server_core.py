#!/usr/bin/env python

###
##  LOGIN SERVER CORE
#  

# Main Imports:
from pandac.PandaModules import QueuedConnectionManager, QueuedConnectionListener
from pandac.PandaModules import QueuedConnectionReader, ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from pandac.PandaModules import NetDatagram
from direct.task.Task import Task
from pandac.PandaModules import *
from db import DataBase
import rencode

# Game Imports:


# Login server Core.
class LoginServer:
	def __init__(self, port, backlog=1000, compress=False):
		self.port = port
		self.backlog = backlog
		self.compress = compress

		self.cManager = QueuedConnectionManager()
		self.cListener = QueuedConnectionListener(self.cManager, 0)
		self.cReader = QueuedConnectionReader(self.cManager, 0)
		self.cWriter = ConnectionWriter(self.cManager,0)
		
		self.db = DataBase()
		# This is for pre-login
		self.tempConnections = []
		# This is for authed clients
		self.activeConnections = []
		
		# Temp user dict
		self.clients={}
		
		self.active_servers=[]
		
		self.connect(self.port, self.backlog)
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
				self.tempConnections.append(newConnection) # Lets add it to a temp list first.
				self.cReader.addConnection(newConnection)     # Begin reading connection
				
				# Make the temp place holder then add to temp, under dataget check the temp list, if something ther do
				# auth and then add to the active
		return Task.cont

	def tskDisconnectPolling(self, task):
		while self.cManager.resetConnectionAvailable() == True:
			print "disconnect"
			connPointer = PointerToConnection()
			self.cManager.getResetConnection(connPointer)
			connection = connPointer.p()
			
			# Remove the connection we just found to be "reset" or "disconnected"
			self.cReader.removeConnection(connection)
			# Remove the connection we just found to be "reset" or "disconnected"
			self.cReader.removeConnection(connection)
			for u in range(len(self.clients)):
				if self.clients[u]:
					if self.clients[u]['connection']==connection:
						del self.clients[u]
						self.clients[u]=False
						break
			
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
		
	# This will check and do the logins.
	def auth(self, datagram): 
		# If in login state.
		clientIp = datagram.getAddress() # This is the ip :P
		clientCon = datagram.getConnection() # This is the connection data. used to send the shit.
		package=self.processData(datagram)
		print "SERVER: ",package
		valid_packet=False
		if len(package)==2:
			# if login request is send reply
			# Should add a checker like in the db something like isLogged(0 or 1)
			# If found then say no for client
			user_found=False
			if package[0]=='login_request':
				valid_packet=True
				print "Try login"
				for u in range(len(self.clients)):
					if self.clients[u]['name']==package[1][0]:
						print "User already exists"
						user_found=True
						data = {}
						data[0] = "error"
						data[1] = "User already logged in"
						self.sendData(data,clientCon)
						break
						# send something back to the client saying to change username
				if not user_found:
					username=package[1][0]
					password=package[1][1]
					self.db.Client_getLogin(username, password)
					if self.db.login_valid:
						# Add the user
						new_user={}
						new_user['name']=package[1][0]
						new_user['connection']=clientCon
						new_user['ready']=False
						new_user['new_dest']=False
						new_user['new_spell']=False
						self.clients[len(self.clients)]=new_user
						# Send back the valid check.
						data={}
						data[0]='login_valid' # If client gets this the client should switch to main_menu.
						data[1]={}
						data[1][0]=self.db.status
						data[1][1]=len(self.clients)-1 # This is part of the old 'which' packet
						self.sendData(data, clientCon)
						return True
				else:
					status = self.db.status
					data={}
					data[0]='db_reply'
					data[1]=status
					self.sendData(data, clientCon)
			# if server add it to the list of current active servers
			if package[0]=='server':
				valid_packet=True
				print 'Server connected: '+package[1]
				print 'From: '+str(datagram.getAddress())
				server={}
				server[0]=package[1]
				server[1]=str(datagram.getAddress())
				self.active_servers.append(server)
			# if authentication from server reply with auth/not auth of username
			if package[0]=='auth':
				valid_packet=True
				client_auth=False
				print 'Attempting Authentication on: '+package[1]
				for u in range(len(self.clients)):
					if self.clients[u]['name']==package[1]:
						client_auth=True
						break
				data = {}
				if client_auth:
					data[0] = 'auth'
				else:
					data[0] = 'fail'
				data[1] = self.clients[u]['name']
				self.sendData(data, clientCon)
			if not valid_packet:
				data = {}
				data[0] = "error"
				data[1] = "Wrong Packet"
				self.sendData(data, clientCon)
				print "Login Packet not correct"
				
		else:
			print "Data in packet wrong size"

	def getData(self):
		data = []
		while self.cReader.dataAvailable():
			datagram = NetDatagram()  # catch the incoming data in this instance
			# Check the return value; if we were threaded, someone else could have
			# snagged this data before we did
			if self.cReader.getData(datagram):
				if datagram.getConnection() in self.tempConnections:
					print "Check Auth!"
					if self.auth(datagram):
						# Move client to the self.activeConnections list.
						self.activeConnections.append(datagram.getConnection())
						print "HERE IS ACTIVE: ", self.activeConnections
						self.tempConnections.remove(datagram.getConnection())
						print "HERE IS TEMP", self.tempConnections
						print self.active_servers
					print "Auth Done!"
					# in auth def or after the connection will be moved to self.activeConnections
					# and then removed from the temp list
					break
				# Check if the data recieved is from a valid client.
				elif datagram.getConnection() in self.activeConnections:
					appendage={}
					appendage[0]=self.processData(datagram)
					appendage[1]=datagram.getConnection()
					data.append(appendage)
				
		return data
