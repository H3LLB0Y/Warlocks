from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

from server import Server
from game import Game

game_tick=1.0/60.0

class ServerInst():
	def __init__(self):
		# Initialise Window
		self.showbase=ShowBase()
		
		# Disable Mouse Control for camera
		self.showbase.disableMouse()
		
		camera.setPos(0,0,100)
		camera.lookAt(0,0,0)
		
		# Start our server up
		self.server = Server(9099, compress=True)
		
		self.users={}
		
		taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')

	# handles new joining clients and updates all clients of chats and readystatus of players
	def lobby_loop(self,task):
		# if in lobby state
		temp=self.server.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package) +" "+ str(package[1].getAddress())
					if len(package[0])==2:
						# if username is sent, assign to client
						if package[0][0]=='username':
							user_found=False
							valid_packet=True
							for u in range(len(self.users)):
								if self.users[u]['name']==package[0][1]:
									print "User already exists"
									user_found=True
									data = {}
									data[0] = "error"
									data[1] = "User already exists"
									self.server.sendData(data,package[1])
									# send something back to the client saying to change username
							if not user_found:
								new_user={}
								new_user['name']=package[0][1]
								new_user['connection']=package[1]
								new_user['ready']=False
								#new_user['warlock']=self.warlock=Warlock(self.showbase,len(self.users))
								new_user['new_dest']=False
								new_user['new_spell']=False
								self.users[len(self.users)]=new_user
								data = {}
								data[0] = "which"
								data[1] = len(self.users)-1
								self.server.sendData(data,package[1])
						# else check to make sure connection has username
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
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
									self.server.broadcastData(data)
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
									self.server.broadcastData(data)
								# break out of for loop
								break
							else:
								print str(self.users[u]['connection'])+" "+str(package[1])
						if not valid_packet:
							data = {}
							data[0] = "error"
							data[1] = "Please Login"
							self.server.sendData(data,package[1])
							print "User not logged in"
					else:
						print "Data in packet wrong size"
				else:
					print "Packet wrong size"
		# if all players are ready and there is X of them
		game_ready=True
		# if there is any clients connected
		if not self.server.getClients():
			game_ready=False
		for u in range(len(self.users)):
			if self.users[u]['ready']==False:
				game_ready=False
		if game_ready:
			data = {}
			data[0]='state'
			data[1]='game'
			self.server.broadcastData(data)
			taskMgr.doMethodLater(0.5, self.pregame_loop, 'Pregame Loop')
			return task.done
		return task.again
		
	def pregame_loop(self,task):
		print "Pregame State"
		self.game_time=0
		self.tick=0
		self.game=Game(len(self.users),game_tick,self.showbase)
		for u in range(len(self.users)):
			self.users[u]['warlock']=self.game.warlock[u]
		taskMgr.doMethodLater(0.5, self.game_loop, 'Game Loop')
		return task.done
		return task.again
		
	def game_loop(self,task):
		# if there is any clients connected
		if self.server.getClients():
			# process incoming packages
			temp=self.server.getData()
			if temp!=[]:
				for i in range(len(temp)):
					valid_packet=False
					package=temp[i]
					if len(package)==2:
						print "Received: " + str(package) +" "+str(package[1])
						if len(package[0])==2:
							print "packet right size"
							# else check to make sure connection has username
							for u in range(len(self.users)):
								if self.users[u]['connection']==package[1]:
									print "Packet from "+self.users[u]['name']
									# process packet
									# if chat packet
									if package[0][0]=='destination':
										print "Destination: "+str(package[0][1])
										valid_packet=True
										# Update warlock data for client
										self.users[u]['warlock'].set_destination(Vec3(package[0][1][0],package[0][1][1],0))
										self.users[u]['new_dest']=True
									elif package[0][0]=='spell':
										print "Spell: "+str(package[0][1])
										valid_packet=True
										# Update warlock data for client
										self.users[u]['warlock'].set_spell(package[0][1][0],package[0][1][1])
										self.users[u]['new_spell']=True
									break
								else:
									print "couldnt find connection"+str(self.users[u]['connection'])+" "+str(package[1])
			# get frame delta time
			dt=globalClock.getDt()
			self.game_time+=dt
			# if time is less than 3 secs (countdown for determining pings of clients)
			# tick out for clients
			if (self.game_time>game_tick):
				# update all clients with new info before saying tick
				for u in range(len(self.users)):
					# new warlock destinations
					if self.users[u]['new_dest']:
						data = {}
						data[0]='update_dest'
						data[1]=u
						data[2]={}
						data[2][0]=self.users[u]['warlock'].destination.getX()
						data[2][1]=self.users[u]['warlock'].destination.getY()
						self.users[u]['new_dest']=False
						self.server.broadcastData(data)
					# new warlock spell
					elif self.users[u]['new_spell']:
						data = {}
						data[0]='update_spell'
						data[1]=u
						data[2]=self.users[u]['warlock'].get_spell()
						data[3]=self.users[u]['warlock'].get_target()
						self.users[u]['new_spell']=False
						self.server.broadcastData(data)
				
				data = {}
				data[0]='tick'
				data[1]=self.tick
				self.server.broadcastData(data)
				self.game_time-=game_tick
				self.tick+=1
				# run simulation
				self.game.run_tick()
			return task.cont
		else:
			taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
			return task.done

si = ServerInst()
run()
