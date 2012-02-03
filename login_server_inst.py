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
from game import Game

# LOGIN OPCODES
# We can add them later.
# like: LOGIN_REQUEST = 0x00

game_tick=1.0/60.0

class LoginInst():
	def __init__(self):
		# Initialise Window
		
		# Dont need window.
		self.showbase=ShowBase()
		
		# Disable Mouse Control for camera
		self.showbase.disableMouse()
		
		#camera.setPos(0,0,350)
		#camera.lookAt(0,0,0)
		
		# Start our server up
		print ""
		print "INIT: LOGIN SERVER...\n"
		self.LoginServer = LoginServer(9098, compress=True)
		self.db = DataBase()
		self.users=self.LoginServer.clients

		
		taskMgr.doMethodLater(0.2, self.lobby_loop, 'Lobby Loop')

	# handles new joining clients and updates all clients of chats and readystatus of players
	def lobby_loop(self,task):
		# if in lobby state
		temp=self.LoginServer.getData()
		if temp!=[]:
			
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package) +" "+ str(package[1].getAddress())
					if len(package[0])==2:
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
								print self.users
								print "Packet from "+self.users[u]['name']
								# process packet
								update_warlocks=False
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
								elif package[0][0]=='ready':
									print self.users[u]['name']+" is ready!"
									self.users[u]['ready']=True
									valid_packet=True
									update_warlocks=True
								# else if unready packet
								elif package[0][0]=='unready':
									print self.users[u]['name']+" is not ready!"
									self.users[u]['ready']=False
									valid_packet=True
									update_warlocks=True
								if update_warlocks:
									data = {}
									data[0]='warlocks'
									data[1]=len(self.users)
									self.LoginServer.broadcastData(data)
								# break out of for loop
								break
							else:
								print str(self.users[u]['connection'])+" "+str(package[1])
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
		# if all players are ready and there is X of them
		game_ready=True
		# if there is any clients connected
		if not self.LoginServer.getClients():
			game_ready=False
		for u in range(len(self.users)):
			if self.users[u]['ready']==False:
				game_ready=False
		if game_ready:
			data = {}
			data[0]='state'
			data[1]='game'
			self.LoginServer.broadcastData(data)
			#taskMgr.doMethodLater(0.5, self.pregame_loop, 'Pregame Loop')
			return task.done
		return task.again
	
	# this will be moved onto the game server itself (as a pregame wait until full/enough peeps and everyone to ready)
	def pregame_loop(self,task):
		print "Pregame State"
		self.game_time=0
		self.tick=0
		self.game=Game(len(self.users),game_tick,self.showbase)
		for u in range(len(self.users)):
			self.users[u]['warlock']=self.game.warlock[u]
		taskMgr.doMethodLater(0.5, self.game_loop, 'Game Loop')
		return task.done
		
		# FROM HERE WILL GO TO GAME SERVER>>>
		#return task.again
		
ls = LoginInst()
run()
