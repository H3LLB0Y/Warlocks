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

from db								import DataBase
from server							import Server
from game							import Game
from spell							import Spell
from spellmanager					import SpellManager

# Client for connection to the main server for saying 'i am running'
# and for getting the auth for people that are joining
from client							import Client
from client_config				import *

game_tick=1.0/30.0

num_users=0

class ServerInst():
	def __init__(self):
		# Initialise Window
		self.showbase=ShowBase()
		
		# Disable Mouse Control for camera
		self.showbase.disableMouse()
		
		# Start our server up
		self.server = Server(9099, compress=True)
		self.db = DataBase()
		
		# Client for connecting to main server for showing exists and receiving clients
		self.client=Client(LOGIN_IP, LOGIN_PORT, compress=True)
		if self.client.getConnected():
			# Setup the un/up sendpacket, this will be changed. later :P
			data = {}
			data[0] = 'server'
			data[1] = 'SERVER NAME'
			self.client.sendData(data)
			self.online=True
			taskMgr.doMethodLater(0.5, self.client_validator, 'Client Validator')
		else:
			# client not connected to login/auth server so exit
			print 'Could not connect to Authentication Server.'
			print 'Server is not in online mode. No Authentication will happen for clients.'
			print 'Restart Server to attempt to connect to Authentication Server.'
			self.online=False
		
		self.users={} # We should send the clients from the lobby to here somehow? or just get it from somewhere...
		
		for i in range(num_users):
			new_user={}
			new_user['name']='cake'
			new_user['connection']='cake'
			new_user['ready']=True
			new_user['new_dest']=False
			new_user['new_spell']=False
			new_user['sync']=True
			if self.online:
				new_user['authenticated']=True
			self.users[len(self.users)]=new_user
		
		camera.setPos(0,0,90+45*num_users)
		camera.lookAt(0,0,0)
		
		# get data from spell server
		self.showbase.spells=[]
		
		# i guess this shit should be in the pregame part, so people can choose their spells based of these
		# also it will need to be created in there from data passed from the server (where it will be procedurally generated)
		# spell0
		spell=Spell()
		spell.damage=10
		spell.target_knockback=20
		spell.self_knockback=0
		spell.range=25
		spell.speed=15
		spell.aoe=False
		spell.aoe_range=0
		spell.targeting=False
		spell.casting_time=0
		spell.interruptable=False
		spell.model=0
		self.showbase.spells.append(spell)
		
		# spell1
		spell=Spell()
		spell.damage=25
		spell.target_knockback=10
		spell.self_knockback=0
		spell.range=50
		spell.speed=25
		spell.aoe=False
		spell.aoe_range=0
		spell.targeting=False
		spell.casting_time=0
		spell.interruptable=False
		spell.model=1
		self.showbase.spells.append(spell)
		
		# spell2
		spell=Spell()
		spell.damage=50
		spell.target_knockback=10
		spell.self_knockback=30
		spell.range=50
		spell.speed=15
		spell.aoe=False
		spell.aoe_range=0
		spell.targeting=False
		spell.casting_time=0
		spell.interruptable=False
		spell.model=0
		self.showbase.spells.append(spell)
		
		# spell3
		spell=Spell()
		spell.model=1
		self.showbase.spells.append(spell)
		
		taskMgr.doMethodLater(0.5, self.pregame_loop, 'Lobby Loop')
	
	# task to listen for allowed clients from server
	def client_validator(self,task):
		temp=self.client.getData()
		if temp!=[]:
			print temp
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					if package[0]=='auth':
						print 'User authenticated: '+package[1]
						new_client=-1
						for u in range(len(self.users)):
							if self.users[u]['name']==package[1]:
								new_client=u
								self.users[u]['authenticated']=True
								data = {}
								data[0] = 'auth'
								data[1] = self.users[u]['name']
								self.server.sendData(data,self.users[u]['connection'])
								for s in range(len(self.showbase.spells)):
									data = {}
									data[0] = 'spell'
									data[1] = self.showbase.spells[s].send()
									self.server.sendData(data,self.users[u]['connection'])
								for c in range(len(self.users)):
									data = {}
									data[0] = 'client'
									data[1] = {}
									data[1][0]=c
									data[1][1]=self.users[c]['name']
									self.server.sendData(data,self.users[u]['connection'])
									data = {}
									data[0] = 'ready'
									data[1] = {}
									data[1][0]=self.users[c]['name']
									if self.users[c]['ready']:
										data[1][1]='Ready'
									else:
										data[1][1]='Unready'
									self.server.sendData(data,self.users[u]['connection'])
								data = {}
								data[0] = 'which'
								data[1] = self.users[u]['which']
								self.server.sendData(data,self.users[u]['connection'])
						for u in range(len(self.users)):
							if not self.users[u]['name']==package[1]:
								data = {}
								data[0] = 'client'
								data[1] = {}
								data[1][0]=new_client
								data[1][1]=self.users[new_client]['name']
								self.server.sendData(data,self.users[u]['connection'])
					elif package[0]=='fail':
						print 'User failed authentication: '+package[1]
						for u in range(len(self.users)):
							if self.users[u]['name']==package[1]:
								del self.users[u]
								break
		return task.again
		
	def pregame_loop(self,task):
		# if in pregame state
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
								new_user['new_dest']=False
								new_user['new_spell']=False
								new_user['sync']=False
								new_user['which']=len(self.users)
								if self.online:
									new_user['authenticated']=False
									data = {}
									data[0] = "auth"
									data[1] = new_user['name']
									self.client.sendData(data)
								self.users[len(self.users)]=new_user
						# else check to make sure connection has username
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
								print "Packet from "+self.users[u]['name']
								# if chat packet
								if package[0][0]=='chat':
									print "Chat: "+package[0][1]
									# Broadcast data to all clients ("username: message")
									data = {}
									data[0]='chat'
									data[1]={}
									data[1][0]=u
									data[1][1]=package[0][1]
									self.server.broadcastData(data)
								# else if ready packet
								elif package[0][0]=='ready':
									print self.users[u]['name']+" is ready!"
									self.users[u]['ready']=True
									data = {}
									data[0] = 'ready'
									data[1] = {}
									data[1][0]=self.users[u]['name']
									data[1][1]='Ready'
									self.server.broadcastData(data)
								# else if unready packet
								elif package[0][0]=='unready':
									print self.users[u]['name']+" is not ready!"
									self.users[u]['ready']=False
									data = {}
									data[0] = 'ready'
									data[1] = {}
									data[1][0]=self.users[u]['name']
									data[1][1]='Unready'
									self.server.broadcastData(data)
								# else if disconnect packet
								elif package[0][0]=='disconnect':
									print self.users[u]['name']+" is disconnecting!"
									del self.users[u]
									"""data = {}
									data[0] = "disconnect"
									data[1] = u
									self.server.broadcastData(data)"""
								# break out of for loop
								break
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
			data[1]='preround'
			self.server.broadcastData(data)
			taskMgr.doMethodLater(0.5, self.preround_loop, 'Preround Loop')
			return task.done
		return task.again
		
	def preround_loop(self,task):
		print "Preround State"
		self.game_time=0
		self.tick=0
		self.showbase.num_warlocks=len(self.users)
		
		self.game=Game(self.showbase,game_tick)
		for u in range(self.showbase.num_warlocks):
			self.users[u]['warlock']=self.game.warlock[u]
		taskMgr.doMethodLater(0.5, self.round_ready_loop, 'Game Loop')
		return task.done
		#return task.again
		
	def round_ready_loop(self,task):
		print "Round ready State"
		
		temp=self.server.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package) +" "+ str(package[1].getAddress())
					if len(package[0])==2:
						for u in range(len(self.users)):
							if self.users[u]['connection']==package[1]:
								if package[0][0]=='round':
									if package[0][1]=='sync':
										self.users[u]['sync']=True
		# if all players are ready and there is X of them
		round_ready=True
		# if there is any clients connected
		for u in range(len(self.users)):
			if self.users[u]['sync']==False:
				print self.users[u]['name']
				round_ready=False
		if round_ready:
			taskMgr.doMethodLater(2.5, self.game_loop, 'Game Loop')
			return task.done
		return task.again
	
	def game_loop(self,task):
		#print "Game State"
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
							#print "packet right size"
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
								#else:
								#	print "couldnt find connection"+str(self.users[u]['connection'])+" "+str(package[1])
			# get frame delta time
			dt=globalClock.getDt()
			self.game_time+=dt
			# if time is less than 3 secs (countdown for determining pings of clients)
			# tick out for clients
			if (self.game_time>game_tick):
				# update all clients with new info before saying tick
				for u in range(self.showbase.num_warlocks):
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
				if not self.game.run_tick():
					print 'Game Over'
			return task.cont
		else:
			#taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
			return task.done

si = ServerInst()
run()
