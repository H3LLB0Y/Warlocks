from warlock						import Warlock
from world							import World
from spellmanager					import SpellManager
from pandac.PandaModules import *
from panda3d.bullet import *

class Game():
	def __init__(self,showbase,tick_time):
		self.tick_time=tick_time
		self.num_warlocks=showbase.num_warlocks
		
		# Bullet shit
		self.worldNP = render.attachNewNode('World')

		# World
		self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
		self.debugNP.show()
		self.debugNP.node().showWireframe(True)
		self.debugNP.node().showConstraints(True)
		self.debugNP.node().showBoundingBoxes(False)
		self.debugNP.node().showNormals(True)

		self.debugNP.showTightBounds()
		self.debugNP.showBounds()

		self.bulletworld = BulletWorld()
		self.bulletworld.setGravity(Vec3(0, 0, 0))# -9.81))
		self.bulletworld.setDebugNode(self.debugNP.node())
		
		self.world=World(showbase,self.num_warlocks,self.worldNP,self.bulletworld)
		
		self.warlocks={}
		self.warlock={}
		for u in range(self.num_warlocks):
			self.warlock[u]=Warlock(showbase,u,self.num_warlocks,self.worldNP,self.bulletworld)
			self.warlocks[u]={}
			self.warlocks[u][0]=self.warlock[u].collNP.getName()
			self.warlocks[u][1]=self.warlock[u]
	
		# spell manager setup in pregame state (receive the spells from the server)
		self.spell_man=showbase.spell_man
		
		self.ticks=0
		
	def run_tick(self):
		not_dead=0
		
		# run each of the warlocks simulations
		for u in range(self.num_warlocks):
			if not self.warlock[u].dead:
				self.warlock[u].update(self.tick_time,self.bulletworld,self.spell_man,self.worldNP,self.warlocks)
				not_dead+=1
			# inside here the casting of spells happens, then once the spell manager takes control of the spell the rest will happen from it after this step
		
		if not_dead==0:
			return False
		
		# run the spells
		self.spell_man.update(self.tick_time,self.warlocks,self.bulletworld)
		
		# run physics (just updates the collisionNP's i think so collision detections can work)
		self.bulletworld.doPhysics(self.tick_time,1)
		
		self.ticks+=1
		
		# raise the lava
		self.world.raise_lava()
		
		return True
