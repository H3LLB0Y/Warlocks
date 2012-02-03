from direct.actor.Actor import Actor
from pandac.PandaModules import *
from util import *
from panda3d.bullet import *
from bitmasks import *

class SpellInst():
	def __init__(self,spell,caster,pos,rot,worldNP,bullet):
		self.spell=spell
		self.caster=caster
		# Load spell model
		self.model=Actor(spell.model)
		
		shape=BulletSphereShape(0.666)
		self.collNP=worldNP.attachNewNode(BulletGhostNode('SpellSphere'))
		self.collNP.setCollideMask(NOTARENA)
		self.collNP.node().addShape(shape)
		self.collNP.setPos(pos+move_forwards(rot,1.0))
		self.collNP.setHpr(Vec3(rot,0,0))
		bullet.attachGhost(self.collNP.node())
		self.collNP.reparentTo(worldNP)
		
		self.bullet=bullet
		
		# Reparent the model to render.
		self.model.reparentTo(self.collNP)
		
		self.distance=0
		
		self.remove_me=False
	
	def __del__(self):
		self.bullet.removeGhost(self.collNP.node())
		self.collNP.removeNode()
		self.model.delete()
	
	def update(self,dt,bulletworld):
		retval=''
		if self.collNP.node().getNumOverlappingNodes()>0:
			for node in self.collNP.node().getOverlappingNodes():
				if node.getName()==self.caster:
					retval='hit owner'
				else:
					retval=node.getName()
		vel=move_forwards(self.collNP.getH(),self.spell.speed)
		self.collNP.setPos(self.collNP.getPos()+vel*dt)
		self.distance+=vel.length()*dt
		if self.distance>self.spell.range:
			retval='over range'
		return retval
