#!/usr/bin/env python

###
##  LOGIN/LOBBY SERVER
#  

from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
	window-type none
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

from db import DataBase
from login_server_core import LoginServer

# LOGIN OPCODES
# We can add them later.
# like: LOGIN_REQUEST = 0x00

class LoginInst():
	def __init__(self):		
		# Dont need window.
		self.showbase=ShowBase()
		
		# Start our server up
		print ""
		print "INIT: LOGIN SERVER...\n"
		self.LoginServer = LoginServer(9098, compress=True)
		print "INIT: DATABASE...\n"
		self.db = DataBase()
		self.users=self.LoginServer.clients
		print self.users, "HERE !!!!!!!!!"
		
		taskMgr.doMethodLater(0.2, self.lobby_loop, 'Lobby Loop')

	# handles new joining clients and updates all clients of chats and readystatus of players
	def lobby_loop(self,task):
		# if in lobby state
		temp=self.LoginServer.getData()
		if temp!=[]:
			#print temp
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					#print "Received: " + str(package) +" "+ str(package[1].getAddress())
					if len(package[0])==2:
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
								#print self.users
								print "Packet from "+self.users[u]['name']
								# if chat packet
								if package[0][0]=='chat':
									print "Chat: "+package[0][1]
									valid_packet=True
									# Broadcast data to all clients ("username: message")
									data = {}
									data[0]='chat'
									data[1]=self.users[u]['name']+": "+package[0][1]
									self.LoginServer.broadcastData(data)
								# else if ready packet
								elif package[0][0]=='server_query':
									for s in self.LoginServer.active_servers:
										print 'server: '+str(s[1])
										data = {}
										data[0] = "server"
										data[1] = str(s[1])
										self.LoginServer.sendData(data,package[1])
									data = {}
									data[0] = "final"
									data[1] = "No more servers"
									self.LoginServer.sendData(data, package[1])
									valid_packet=True
							else:
								print 'packet from server'
								#print str(self.users[u]['connection'])+" "+str(package[1])
						if not valid_packet:
							data = {}
							data[0] = "error"
							data[1] = "Please Login"
							self.LoginServer.sendData(data,package[1])
							print "User not logged in"
					else:
						print "Data in packet wrong size"
				else:
					print "Packet wrong size"
		return task.again
		
ls = LoginInst()
run()
