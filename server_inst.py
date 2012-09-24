from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from server							import Server

game_tick = 1.0 / 30.0

class ServerInst():
	def __init__(self):
		# Start our server up
		self.server = Server()
		
		self.server.attempt_authentication()
		
		taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
		
	def lobby_loop(self, task):
		temp = self.server.getData()
		if temp != []:
			for package in temp:
				if len(package) == 2:
					print "Received: ", str(package)
					packet = package[0]
					connection = package[1]
					if len(packet) == 2:
						# check to make sure connection has username
						for user in self.server.users:
							if user.connection == connection:
								# if chat packet
								if packet[0] == 'chat':
									print 'Chat: ', packet[1]
									# Broadcast data to all clients ("username: message")
									self.server.broadcastData(('chat', (user.name, packet[1])))
								# else if ready packet
								elif packet[0] == 'ready':
									print user.name, ' changed readyness!'
									user.ready = packet[1]
									self.server.broadcastData(('ready', (user.name, user.ready)))
								# else if disconnect packet
								elif packet[0] == 'disconnect':
									print user.name, ' is disconnecting!'
									self.server.users.remove(user)
									self.server.broadcastData(('disconnect', user.name))
								# break out of for loop
								break
		# if all players are ready and there is X of them
		game_ready = True
		# if there is any clients connected
		if self.server.getUsers() == []:
			game_ready = False
		for user in self.server.users:
			if not user.ready:
				game_ready = False
		if game_ready:
			self.server.broadcastData(('state', 'preround'))
			self.server.client.sendData(('state', 'preround'))
			taskMgr.doMethodLater(0.5, self.preround_loop, 'Preround Loop')
			return task.done
		return task.again
		
	def preround_loop(self,task):
		print "Preround State"
		self.game_time = 0
		self.tick = 0

		users = []
		for user in self.server.users:
			users.append(user.gameData)
		self.server.game.init_game(self.server, game_tick, users)
		taskMgr.doMethodLater(0.5, self.round_ready_loop, 'Game Loop')
		return task.done
		#return task.again
		
	def round_ready_loop(self,task):
		print "Round ready State"
		temp = self.server.getData()
		if temp != []:
			for package in temp:
				if len(package) == 2:
					print "Received: ", str(package)
					if len(package[0]) == 2:
						for user in self.server.users:
							if user.connection == package[1]:
								if package[0][0] == 'round':
									if package[0][1] == 'sync':
										user.sync = True
		# if all players are ready and there is X of them
		round_ready = True
		# if there is any clients connected
		for user in self.server.users:
			if user.sync == False:
				print user.name
				round_ready = False
		if round_ready:
			taskMgr.doMethodLater(2.5, self.game_loop, 'Game Loop')
			return task.done
		return task.again
	
	def game_loop(self,task):
		print "Game State"
		# process incoming packages
		temp = self.server.getData()
		if temp != []:
			for package in temp:
				if len(package) == 2:
					print "Received: " + str(package)
					if len(package[0]) == 2:
						# check to make sure connection has username
						for user in self.server.users:
							if user.connection == package[1]:
								user.gameData.processUpdatePacket(package[0])
		# get frame delta time
		dt = globalClock.getDt()
		self.game_time += dt
		# if time is less than 3 secs (countdown for determining pings of clients)
		# tick out for clients
		if self.game_time > game_tick:
			# update all clients with new info before saying tick
			for user in self.server.users:
				updates = user.gameData.makeUpdatePackets()
				if updates == None:
					continue
				for packet in updates:
					self.server.broadcastData((user.name, packet))
			self.server.broadcastData(('tick', self.tick))
			self.game_time -= game_tick
			self.tick += 1
			# run simulation
			if not self.server.game.run_tick():
				print 'Game Over'
		return task.cont

si = ServerInst()
run()
