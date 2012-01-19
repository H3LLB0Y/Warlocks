from warlock						import Warlock
from world							import World

class Game():
	def __init__(self,num_warlocks,tick_time,showbase):
		self.tick_time=tick_time
		self.num_warlocks=num_warlocks
		
		self.world=World(showbase)
		
		self.warlock={}
		for u in range(self.num_warlocks):
			self.warlock[u]=Warlock(showbase,u,self.num_warlocks)
		
		self.ticks=0
		
	def run_tick(self):
		# here implement some kind of sliding phyiscs based on damage taken already
		# so heaps of damage means they keep sliding longer less friction
		for u in range(self.num_warlocks):
			self.warlock[u].update(self.tick_time)
		# implement game loop so its same code for server and client
		# receive updates to warlock and move him
		
		self.ticks+=1
		# raise the lava
		self.world.raise_lava()
