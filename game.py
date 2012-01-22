from warlock						import Warlock
from world							import World
from pandac.PandaModules import *

class Game():
	def __init__(self,num_warlocks,tick_time,showbase):
		self.tick_time=tick_time
		self.num_warlocks=num_warlocks
		
		# Create a traverser that Panda3D will automatically use every frame.
		base.cTrav=CollisionTraverser()
		# Initialize the handler for the events.
		self.collHandEvent = CollisionHandlerEvent()
		self.collHandEvent.addInPattern('%fn-into-%in')
		self.collHandEvent.addAgainPattern('%fn-again-%in')
		self.collHandEvent.addOutPattern('%fn-out-%in')
		
		# Define a few bitmasks for use.
		warlockWorldMask = BitMask32(0x1) # for collisions between the warlocks down rays and the world polygons
		warlockMask = BitMask32(0x2) # for collisions between the warlocks down rays and the world polygons
		
		self.world=World(showbase,num_warlocks)
		self.world.n_col.node().setIntoCollideMask(warlockWorldMask)
		
		self.world_warlock_str={}
		
		self.warlock={}
		for u in range(self.num_warlocks):
			self.warlock[u]=Warlock(showbase,u,self.num_warlocks)
			self.warlock[u].down.node().setFromCollideMask(warlockWorldMask)
			self.warlock[u].colNode.node().setCollideMask(warlockMask)
			base.cTrav.addCollider(self.warlock[u].down,self.collHandEvent)
			showbase.accept(self.warlock[u].ray_str+'-out-'+'world_col',self.on_lava)
			showbase.accept(self.warlock[u].ray_str+'-into-'+'world_col',self.off_lava)
			# build a dictionary (kind of a map i guess, the name of the collNode is the key, warlock is the data) for comparison with the collision entry 
			self.world_warlock_str[u]={}
			self.world_warlock_str[u][0]=self.warlock[u].ray_str
			self.world_warlock_str[u][1]=self.warlock[u]
		
		base.cTrav.showCollisions(render)
		
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
		
	def off_lava(self, collEntry):
		for u in range(self.num_warlocks):
			if self.world_warlock_str[u][0]==collEntry.getFromNodePath().getName():
				print "Warlock "+str(u)+' is off lava'
				self.world_warlock_str[u][1].is_on_lava(False)
	
	def on_lava(self, collEntry):
		for u in range(self.num_warlocks):
			if self.world_warlock_str[u][0]==collEntry.getFromNodePath().getName():
				print "Warlock "+str(u)+' is on lava'
				self.world_warlock_str[u][1].is_on_lava(True)
