from math import pi, sin, cos, atan2, floor, degrees
from direct.actor.Actor import Actor
from pandac.PandaModules import Vec3, CollisionSphere, CollisionNode
from direct.showbase.PythonUtil import fitDestAngle2Src

from pandac.PandaModules import *
from util import *
import math
from panda3d.bullet import *

# Warlock Class
class Warlock():
	index = 0
	# Setup function for Warlock
	def __init__(self, showbase, num_warlocks, worldNP, bullet):
		# Load warlock model
		self.model = Actor('media/warlock/warlock')
		# Reparent the model to render.
		self.model.reparentTo(render)
		
		self.num_warlocks = num_warlocks
		
		# rotation between each warlock for even spacing
		rotation = 360.0 / num_warlocks
		# adjust rotation for this warlock
		rotation *= (Warlock.index + 1)
		
		shape = BulletCylinderShape(1.25, 3.5, ZUp)
		self.collNP = worldNP.attachNewNode(BulletGhostNode('Warlock' + str(Warlock.index)))
		self.collNP.setPos(move_forwards(rotation, -5.0 * num_warlocks) + Vec3(0, 0, 1.75))
		self.collNP.setHpr(Vec3(rotation, 0, 0))
		self.collNP.setCollideMask(BitMask32.allOn())
		self.collNP.node().addShape(shape)
		bullet.attachGhost(self.collNP.node())
		self.collNP.reparentTo(worldNP)
		
		# set its position 10*num_warlocks units from center and face warlock to center
		self.model.setPos(-Vec3(0, 0, 2.25))
		self.model.reparentTo(self.collNP)
		
		# destination (will be flag model or something eventually)
		self.destination = (self.model.getPos())
		self.moving = False
		self.dest_node = showbase.loader.loadModel('media/warlock/dest/dest')
		# Reparent the model to render
		self.dest_node.reparentTo(render)
		self.dest_node.setScale(0.25)
		self.dest_node.setZ(-10)
		
		# initialise warlock spell stuff
		self.spell = 0
		self.spell_target = Vec3(0, 0, 0)
		self.casting = False
		
		# physics velocities (one for movement to destination, other for knock around caused by spells)
		self.dest_vel = Vec3(0, 0, 0)
		self.spell_vel = Vec3(0, 0, 0)
		# damage taken by warlock affects the friction applied to them, more damage == more slidey
		self.friction = 1.0
		
		# variable to track if warlock is on lava or still on arena
		self.on_lava = False
		
		# hit points of warlock
		self.hp = 100.0
		self.dead = False
		
		Warlock.index += 1
		
	# for client to attach ring below clients warlock
	def attach_ring(self, showbase):
		self.ring_node = showbase.loader.loadModel('media/warlock/warlock_ring')
		self.ring_node.setPos(-Vec3(0, 0, 1.25))
		self.ring_node.reparentTo(self.collNP)
		
	def set_destination(self, destination):
		# set destination of warlock to input
		self.destination = Vec3(destination[0], destination[1], 0)
		#self.destination.setX(clamp(self.destination.getX(),-80,80))
		#self.destination.setY(clamp(self.destination.getY(),-80,80))
		self.dest_node.setPos(self.destination)
		self.moving = True
		self.casting = False
	
	def get_destination_update(self):
		return self.destination.getX(), self.destination.getY()
	
	# set warlock to spell cast mode
	def set_spell(self, spell):
		self.spell = spell[0]
		self.spell_target = Vec3(spell[1][0], spell[1][1], 0)
		self.dest_node.setZ(-10)
		self.moving = False
		self.casting = True
	
	def get_spell_update(self):
		return self.spell, (self.spell_target.getX(), self.spell_target.getY())
	
	# turn warlock to face destination/target
	def adjust_angle(self, angle, dt):
		targetH = angle
		oldH = self.collNP.getH()
		targetH = fitDestAngle2Src(oldH, targetH)
		magnitude = abs(targetH - oldH) + 90.0
		if magnitude > 95.0:
			if targetH - oldH < 0:
				self.collNP.setH((self.collNP.getH() - (magnitude * 2.5 * dt)) % 360)
			else:
				self.collNP.setH((self.collNP.getH() + (magnitude * 2.5 * dt)) % 360)
		else:
			self.collNP.setH((self.collNP.getH() + (targetH - oldH)) % 360)
		# turns with speed relating to difference in angle (too slow when low angles i think)
		#self.setH(self,(3*(targetH-oldH)*dt)%360)
		
	# will be for knock around caused by spells
	def set_spell_vel(self, spell_vel):
		self.spell_vel.setX(spell_vel.getX())
		self.spell_vel.setY(spell_vel.getY())
	
	# will be for knock around caused by spells
	def add_spell_vel(self, spell_vel):
		self.spell_vel.setX(self.spell_vel.getX() + spell_vel.getX())
		self.spell_vel.setY(self.spell_vel.getY() + spell_vel.getY())
	
	# will be for knock around caused by spells
	def get_spell_vel(self):
		return self.spell_vel
	
	def get_vel_mag(self):
		return self.spell_vel.length() + self.dest_vel.length()
		
	# will be for hp caused by spells
	def remove_hp(self, hp):
		self.hp -= hp
	
	# will be for friction caused by spells
	def add_friction(self, friction):
		self.friction += friction
		
	def get_friction(self):
		return self.friction
	
	# update function for warlock, processes physics and movement/turning of warlock
	def update(self, dt, bulletworld, spell_man, worldNP, usersData):
		if self.friction < 1.0:
			self.friction = 1.0
		if self.friction > 1000.0:
			self.friction = 1000.0
		
		# develocitize the destination velocity (slow it down, will get reset if it is still going to destination
		if self.dest_vel.length() < 1.0:
			self.dest_vel.setX(0.0)
			self.dest_vel.setY(0.0)
		else:
			minus = VBase3(self.dest_vel)
			if minus.normalize():
				self.dest_vel.setX(self.dest_vel.getX() - minus.getX())
				self.dest_vel.setY(self.dest_vel.getY() - minus.getY())
		# decrease spell velocity (friction)
		if self.spell_vel.length() < 1.0:
			self.spell_vel.setX(0)
			self.spell_vel.setY(0)
		else:
			minus = VBase3(self.spell_vel)
			if minus.normalize():
				self.spell_vel.setX(self.spell_vel.getX() - minus.getX())
				self.spell_vel.setY(self.spell_vel.getY() - minus.getY())
		
		# if spell is being cast
		if self.casting:
			# calculate difference in angles between warlock and destination
			self.diff_angle = ((atan2(self.spell_target.getY() - self.collNP.getY(), self.spell_target.getX() - self.collNP.getX()) * (180 / pi)) + 270.0) % 360.0
			# turn to face target
			self.adjust_angle(self.diff_angle,dt)
			self.diff_angle = (self.diff_angle - self.collNP.getH() + 360.0) % 360.0
			# if facing target
			if self.diff_angle < 0.5 or self.diff_angle > 359.5:
				# cast spell
				self.casting = False # but in this case we are just saying spell is done :D
				# run animation to for casting spell
				# once animation is finished then cast spell
				spell_man.cast_spell(self.spell, self.collNP.getName(), self.collNP.getPos(), self.collNP.getH(), worldNP, bulletworld)
				self.add_spell_vel(move_forwards(self.collNP.getH(), spell_man.spells[self.spell].self_knockback))
		# else if moving to new destination
		elif self.moving:
			distance = self.model.getDistance(self.dest_node)
			self.dest_node.setH(self.collNP.getH())
			# if warlock has reached destination
			if distance < 2.5:
				self.moving = False
				self.dest_node.setZ(-10)
				# set animation to idle
			else:
				# calculate difference in angles between warlock and destination
				self.diff_angle = ((atan2(self.destination.getY() - self.collNP.getY(), self.destination.getX() - self.collNP.getX()) * (180 / pi)) + 270.0) % 360.0
				# turn to face target
				self.adjust_angle(self.diff_angle, dt)
				# increase movement vector in direction of destination (limit to a max speed from this, physics can make it more)
				# so if its already more, dont increase, only if it is less
				if distance > 12.5:
					distance = 12.5
				# for if the movement will be straight relative to the player
				self.dest_vel = move_forwards(self.collNP.getH(), distance)
		
		hit_warlock = False
		#check for collisions with other warlocks
		if self.collNP.node().getNumOverlappingNodes() > 0:
			for node in self.collNP.node().getOverlappingNodes():
				for user in usersData:
					name = user.warlock.collNP.getName()
					if node.getName() == name:
						hit_warlock = True
						print 'hit warlock ', name
		
		#if not hit_warlock:
		# process velocitys from both destination
		self.collNP.setX(self.collNP.getX() + self.dest_vel.getX() * dt)
		self.collNP.setY(self.collNP.getY() + self.dest_vel.getY() * dt)
		# and spells
		self.collNP.setX(self.collNP.getX() + self.spell_vel.getX() * dt)
		self.collNP.setY(self.collNP.getY() + self.spell_vel.getY() * dt)
		
		pFrom = self.collNP.getPos()
		pTo = Point3(pFrom + Point3(0.0, 0.0, -10.0))
		result = bulletworld.rayTestClosest(pFrom, pTo)
		# if it does not hit arena then it must be on lava
		if result.hasHit():
			self.on_lava = False
		else:
			self.on_lava = True
		
		if self.on_lava:
			self.hp -= 0.5
			self.friction += 5
		
		if self.hp <= 0:
			self.dead = True
			self.collNP.setZ(-10) # remove player from the arena
