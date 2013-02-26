#from math import pi, sin, cos, atan2
#from direct.showbase.ShowBase import ShowBase
#from direct.task import Task
#import sys, random
#from pandac.PandaModules import *
#from direct.gui.DirectGui import *
#from panda3d.core import TextNode
#from direct.showbase.DirectObject import DirectObject
from collections import deque

from util							import *
from game							import Game, GameHandler

game_tick = 1.0 / 30.0

class Round():
	# Initialisation Function
	def __init__(self, showbase):
		# Initialise Window
		self.showbase = showbase
		
		# total time since start of game, to keep ticks updating on time (rather, not before)
		self.total_time = 0
		
		# packets queue
		self.incoming = deque()
		
		users = []
		for user in self.showbase.users:
			if user.name == self.showbase.username:
				user.gameData.thisPlayer = True
			users.append(user.gameData)
		self.showbase.game = Game(self.showbase, users, self.showbase.gameData)
		self.gameHandler = GameHandler(self.showbase, self.showbase.game)
		
		self.tick = 0
		self.temp_tick = 0
		
		# Set event handlers for keys		
		#self.showbase.accept("escape", sys.exit)
		
		# send loading completion packet to the game server
		self.showbase.client.sendData(('round', 'sync'))
		
		# Add the game loop procedure to the task manager.
		self.showbase.taskMgr.add(self.game_loop, 'Game Loop')
		
	# Game Loop Procedure
	def game_loop(self, task):
		dt = globalClock.getDt()
		# update total time
		self.total_time += dt
		# process any incoming network packets
		temp = self.showbase.client.getData()
		for packet in temp:
			# this part puts the next packets onto the end of the queue
			self.incoming.append(packet)
		
		# while there is packets to process
		while len(self.incoming):
			package = self.incoming.popleft()
			if len(package) == 2:
				# if username is sent, assign to client
				if package[0] == 'tick':
					# not sure if this is the best way to do this but yea something to look into for syncing them all preround i guess
					if package[1] == 0:
						self.total_time = 0
					# check what tick it should be
					self.temp_tick = package[1]
					# if this tick needs to be run (if frames are up to the server tick)
					#if self.temp_tick * game_tick <= self.total_time:
						# run tick
					if not self.showbase.game.run_tick(game_tick):
						print 'Game Over'
					#else:
						# otherwise put packet back on front of list and end frame processing
					#	self.incoming.appendleft(package)
					#	break
				else:
					for user in self.showbase.users:
						if user.name == package[0]:
							user.gameData.processUpdatePacket(package[1])
		self.gameHandler.update(dt)
			
		# Return cont to run task again next frame
		return task.cont
