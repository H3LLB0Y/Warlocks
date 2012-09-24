from warlock						import Warlock
from world							import World
from spell							import Spell
from spellmanager					import SpellManager
from CameraHandler					import CameraHandler
from skybox							import Skybox
from util							import *
from pandac.PandaModules import *
from panda3d.bullet import *
from direct.gui.OnscreenText import OnscreenText

#from db							import SpellDataBase

class GameData():
	def __init__(self):
		self.destination = (-1, -1)
		self.new_dest = False
		self.spell = -1
		self.target = (-1, -1)
		self.new_spell = False
		self.warlock = None
		self.dead = False
		self.thisPlayer = False

	def makeUpdatePackets(self):
		packets = []
		# new destination
		if self.new_dest:
			packets.append(('update_dest', self.destination))
			self.new_dest = False
		# new spell
		if self.new_spell:
			packets.append(('update_spell', (self.spell, self.target)))
			self.new_spell = False

	def processUpdatePacket(self, packet):
		if packet[0] == 'update_dest':
			self.destination = packet[1]
			self.new_dest = True
		elif packet[0] == 'update_spell':
			self.spell = packet[1][0]
			self.target = packet[1][1]
			self.new_spell = True

class GameHandler():
	def __init__(self, showbase, game):
		self.client = showbase.client
		self.game = game

		# Keys array (down if 1, up if 0)
		self.keys = { "left": 0, "right": 0, "up": 0, "down": 0, "c": 0, "x": 0 }
		
		# holding c will focus the camera on clients warlock
		showbase.accept("c", set_value, [self.keys, "c", 1])
		showbase.accept("c-up", set_value, [self.keys, "c", 0])
		
		# variable to track which spell has been requested
		self.current_spell = -1
		
		# keys to change spell
		showbase.accept("q", self.set_spell, [0])
		showbase.accept("w", self.set_spell, [1])
		showbase.accept("e", self.set_spell, [2])
		showbase.accept("r", self.set_spell, [3])
		
		# mouse 1 is for casting the spell set by the keys
		showbase.accept("mouse1", self.cast_spell)
		
		# mouse 3 is for movement, or canceling keys for casting spell
		showbase.accept("mouse3", self.update_destination)
		
		self.skybox = Skybox(showbase)
		
		self.ch = CameraHandler()
		
		# this is unnecessary lol but meh ill comment it anyway
		self.hp = OnscreenText(text = "HP: "+str(100.0), pos = (0.95,-0.95), 
											scale = 0.07,fg=(1,1,1,1),align=TextNode.ACenter,mayChange=1)
		
		# sets the camera up behind clients warlock looking down on it from angle
		follow = self.game.warlock.warlock.model
		self.ch.setTarget(follow.getPos().getX(),follow.getPos().getY(),follow.getPos().getZ())
		self.ch.turnCameraAroundPoint(follow.getH(),0)
	
	def set_spell(self, spell):
		self.current_spell = spell
	
	# sends spell request to server if one is selected
	def cast_spell(self):
		if not self.current_spell == -1:
			target = self.ch.get_mouse_3d()
			if not target.getZ() == -1:
				self.client.sendData(('spell', (self.current_spell, (target.getX(), target.getY()))))
				self.current_spell = -1
	
	# sends destination request to server, or cancels spell if selected
	def update_destination(self):
		if self.current_spell == -1:
			destination = self.ch.get_mouse_3d()
			if not destination.getZ() == -1:
				self.client.sendData(('destination', (destination.getX(), destination.getY())))
		else:
			self.current_spell = -1

	def update_camera(self, dt):
		# sets the camMoveTask to be run every frame
		self.ch.camMoveTask(dt)
		
		# if c is down update camera to always be following on the warlock
		if self.keys["c"]:
			follow = self.game.warlock.warlock.model
			self.ch.setTarget(follow.getPos().getX(), follow.getPos().getY(), follow.getPos().getZ())
			self.ch.turnCameraAroundPoint(0, 0)

class Game():
	def __init__(self, isServer = False):
		self.spells = []

		if isServer:
			# get data from spell server
			
			# spell0
			spell = Spell()
			spell.damage = 15
			spell.target_knockback = 60
			spell.self_knockback = 0
			spell.range = 25
			spell.speed = 15
			spell.aoe = False
			spell.aoe_range = 0
			spell.targeting = False
			spell.casting_time = 0
			spell.interruptable = False
			spell.model = 0
			self.spells.append(spell)
			
			# spell1
			spell=Spell()
			spell.damage=35
			spell.target_knockback=30
			spell.self_knockback=-10
			spell.range=50
			spell.speed=25
			spell.aoe=False
			spell.aoe_range=0
			spell.targeting=False
			spell.casting_time=0
			spell.interruptable=False
			spell.model=1
			self.spells.append(spell)
			
			# spell2
			spell=Spell()
			spell.damage=50
			spell.target_knockback=10
			spell.self_knockback=30
			spell.range=50
			spell.speed=20
			spell.aoe=False
			spell.aoe_range=0
			spell.targeting=False
			spell.casting_time=0
			spell.interruptable=False
			spell.model=0
			self.spells.append(spell)
			
			# spell3
			spell=Spell()
			spell.model=1
			self.spells.append(spell)

	def packageData(self):
		data = []
		for spell in self.spells:
			data.append(('spell', spell.send()))
		return data

	def unpackageData(self, data):
		for package in data:
			if package[0] == 'spell':
				self.spells.append(Spell(package[1]))

	def init_game(self, showbase, tick_time, warlocks):
		self.tick_time = tick_time
		self.warlocks = warlocks
		
		# Bullet shit
		self.worldNP = render.attachNewNode('World')

		# World
		'''
		self.debugNP = self.worldNP.attachNewNode(BulletDebugNode('Debug'))
		self.debugNP.show()
		self.debugNP.node().showWireframe(True)
		self.debugNP.node().showConstraints(True)
		self.debugNP.node().showBoundingBoxes(False)
		self.debugNP.node().showNormals(True)

		self.debugNP.showTightBounds()
		self.debugNP.showBounds()
		'''
		self.bulletworld = BulletWorld()
		self.bulletworld.setGravity(Vec3(0, 0, 0))# -9.81))
		#self.bulletworld.setDebugNode(self.debugNP.node())
		
		self.world = World(showbase, len(self.warlocks), self.worldNP, self.bulletworld)
		
		u = 0
		for warlock in self.warlocks:
			warlock.warlock = Warlock(showbase, u, len(self.warlocks), self.worldNP, self.bulletworld)
			if warlock.thisPlayer:
				warlock.warlock.attach_ring(showbase)
				self.warlock = warlock
			u += 1
	
		# spell manager setup in pregame state (receive the spells from the server in pregame loading)
		self.spell_man = SpellManager(len(self.warlocks))
		for spell in self.spells:
			self.spell_man.add_spell(spell)
		
		self.ticks = 0
		
	def run_tick(self):
		# run each of the warlocks simulations
		for warlock in self.warlocks:
			if not warlock.dead:
				warlock.warlock.update(self.tick_time, self.bulletworld, self.spell_man, self.worldNP, self.warlocks)
			# inside here the casting of spells happens, then once the spell manager takes control of the spell the rest will happen from it after this step
		
		# run the spells
		self.spell_man.update(self.tick_time, self.warlocks, self.bulletworld)
		
		# run physics (just updates the collisionNP's i think so collision detections can work)
		self.bulletworld.doPhysics(self.tick_time, 1)
		
		self.ticks += 1
		
		# raise the lava
		self.world.raise_lava()
		
		return True
