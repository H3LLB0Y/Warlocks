from math import pi, sin, cos, atan2, floor, degrees
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3, CollisionSphere, CollisionNode
from direct.showbase.PythonUtil import fitDestAngle2Src

from pandac.PandaModules import *
from util import *
import math

# Warlock Class
class Warlock(Actor):
	# Setup function for Warlock
	def __init__(self,showbase,index,num_warlocks):
		# Load warlock model
		Actor.__init__(self,"media/warlock/warlock")
		# Reparent the model to render.
		self.reparentTo(render)
		
		# rotation between each warlock for even spacing
		rotation=360.0/num_warlocks
		# adjust rotation for this warlock
		rotation*=(index+1)
		
		# set its position 80 units from center and face warlock to center
		self.setPos(move_forwards(rotation,-80.0))
		self.setHpr(Vec3(rotation,0,0))
		
		# destination (will be flag model or something eventually)
		self.destination=(self.getPos())
		self.new_destination=False
		self.dest_node=showbase.loader.loadModel("media/warlock/dest/dest")
		# Reparent the model to render
		self.dest_node.reparentTo(render)
		self.dest_node.setScale(0.25)
		self.dest_node.setZ(-10)
		
		# initialise warlock spell stuff
		self.spell=0
		self.spell_target=Vec3(0,0,0)
		self.casting=False
		
		# physics velocities (one for movement to destination, other for knock around caused by spells)
		self.dest_vel=Vec3(0,0,0)
		self.spell_vel=Vec3(0,0,0)
		# damage taken by warlock affects the friction applied to them, more damage == more slidey
		self.damage=1
		
		# hit points of warlock
		self.hp=100.0
		
		# collision sphere for collision detection
		self.colSphere = CollisionSphere(0, 0, 2.5, 3)
		self.colNode = self.attachNewNode(CollisionNode('playerNode'))
		self.colNode.node().addSolid(self.colSphere)
		self.colNode.show()
		
	# for client to attach ring below clients warlock
	def attach_ring(self,showbase):
		self.ring_node=showbase.loader.loadModel("media/warlock/warlock_ring")
		self.ring_node.reparentTo(self)
		
	def set_destination(self,destination):
		# set destination of warlock to input
		self.destination=destination
		self.destination.setX(clamp(self.destination.getX(),-80,80))
		self.destination.setY(clamp(self.destination.getY(),-80,80))
		self.new_destination=True
		self.dest_node.setPos(self.destination)
		self.casting=False
	
	def get_spell(self):
		return self.spell
	
	def get_target(self):
		return [self.spell_target.getX(),self.spell_target.getY()]
	
	# set warlock to spell cast mode
	def set_spell(self,spell,target):
		self.spell=spell
		self.spell_target=Vec3(target[0],target[1],0)
		self.dest_node.setZ(-10)
		self.new_destination=False
		self.casting=True
	
	# turn warlock to face destination/target
	def adjust_angle(self,angle,dt):
		targetH = angle
		oldH = self.getH()
		targetH = fitDestAngle2Src(oldH,targetH)
		magnitude = abs(targetH-oldH)+90.0
		if magnitude>92.5:
			if (targetH-oldH)<0:
				self.setH((self.getH()-(magnitude*2.5*dt))%360)
			else:
				self.setH((self.getH()+(magnitude*2.5*dt))%360)
		else:
			self.setH((self.getH()+(targetH-oldH))%360)
		# turns with speed relating to difference in angle (too slow when low angles i think)
		#self.setH(self,(3*(targetH-oldH)*dt)%360)
	
	# will be for knock around caused by spells
	def add_spell_vel(self,spell_vel):
		self.spell_vel.setX(self.spell_vel.getX()+spell_vel.getX())
		self.spell_vel.setY(self.spell_vel.getY()+spell_vel.getY())
	
	# will be for damage caused by spells
	def add_damage(self,damage):
		self.damage+=damage
	
	# update function for warlock, processes physics and movement/turning of warlock
	def update(self,dt):
		self.dest_node.setH(self.getH())
		if self.damage<1:
			self.damage=1
		
		# develocitize the destination velocity (slow it down, will get reset if it is still going to destination
		self.dest_vel.setX(self.dest_vel.getX()*(1-2.5*dt))
		self.dest_vel.setY(self.dest_vel.getY()*(1-2.5*dt))
		
		# if spell is being cast
		if self.casting:
			# calculate difference in angles between warlock and destination
			self.diff_angle = ((atan2(self.spell_target.getY()-self.getY(),self.spell_target.getX()-self.getX()) * (180 / pi)) + 270.0)%360.0
			# turn to face target
			self.adjust_angle(self.diff_angle,dt)
			# if facing target
			if (self.diff_angle<10):
				# cast spell
				self.casting=False # but in this case we are just saying spell is done :D
		# else if moving to new destination
		elif self.new_destination:
			distance=self.getDistance(self.dest_node)
			# if warlock has reached destination
			if distance<1.5:
				self.new_destination=False
				self.dest_node.setZ(-10)
				# set animation to idle
			else:
				# calculate difference in angles between warlock and destination
				self.diff_angle = ((atan2(self.destination.getY()-self.getY(),self.destination.getX()-self.getX()) * (180 / pi)) + 270.0)%360.0
				# turn to face target
				self.adjust_angle(self.diff_angle,dt)
				# increase movement vector in direction of destination (limit to a max speed from this, physics can make it more)
				# so if its already more, dont increase, only if it is less
				if distance>12.5:
					distance=12.5
				self.dest_vel=move_forwards(self.getH(),distance)
		
		# decrease spell velocity (friction)
		self.spell_vel.setX(self.spell_vel.getX()*(1-1.25*dt*(5.0/self.damage)))
		self.spell_vel.setY(self.spell_vel.getY()*(1-1.25*dt*(5.0/self.damage)))
		
		# process velocitys from both destination
		self.setX(self.getX()+self.dest_vel.getX()*dt)
		self.setY(self.getY()+self.dest_vel.getY()*dt)
		# and spells
		self.setX(self.getX()+self.spell_vel.getX()*dt)
		self.setY(self.getY()+self.spell_vel.getY()*dt)
