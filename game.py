from world							import World
from warlock						import Warlock
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
		self.hp = OnscreenText(text = "HP: " + str(100.0), pos = (0.95, -0.95), 
								scale = 0.07, fg = (1, 1, 1, 1), align = TextNode.ACenter, mayChange = 1)
		
		# sets the camera up behind clients warlock looking down on it from angle
		follow = self.game.warlock.collNP
		self.ch.setTarget(follow.getPos().getX(), follow.getPos().getY(), follow.getPos().getZ())
		self.ch.turnCameraAroundPoint(follow.getH(), 0)
	
	def set_spell(self, spell):
		self.current_spell = spell
	
	# sends spell request to server if one is selected
	def cast_spell(self):
		if not self.current_spell == -1:
			target = self.ch.get_mouse_3d()
			if not target.getZ() == -1:
				self.client.sendData(('update_spell', (self.current_spell, (target.getX(), target.getY()))))
				self.current_spell = -1
	
	# sends destination request to server, or cancels spell if selected
	def update_destination(self):
		if self.current_spell == -1:
			destination = self.ch.get_mouse_3d()
			if not destination.getZ() == -1:
				self.client.sendData(('update_dest', (destination.getX(), destination.getY())))
		else:
			self.current_spell = -1

	def update_camera(self, dt):
		# sets the camMoveTask to be run every frame
		self.ch.camMoveTask(dt)
		
		# if c is down update camera to always be following on the warlock
		if self.keys["c"]:
			follow = self.game.warlock.collNP
			self.ch.setTarget(follow.getPos().getX(), follow.getPos().getY(), follow.getPos().getZ())
			self.ch.turnCameraAroundPoint(0, 0)

	def update(self, dt):
		self.update_camera(dt)
		self.hp.setText("HP: " + str(self.game.warlock.hp))
		# there should be a HUD class which will show all the info needed for the player (like hps,spells cds, etc)

class Game():
	def __init__(self, showbase, usersData, gameData):
		self.usersData = usersData
		
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
		
		self.world = World(showbase, len(self.usersData), self.worldNP, self.bulletworld)
		
		for user in self.usersData:
			user.warlock = Warlock(showbase, len(self.usersData), self.worldNP, self.bulletworld)
			if user.thisPlayer:
				self.warlock = user.warlock
				self.warlock.attach_ring(showbase)
	
		# spell manager setup in pregame state (receive the spells from the server in pregame loading)
		self.spell_man = SpellManager()
		for spell in gameData.spells:
			self.spell_man.add_spell(spell)
		
		self.ticks = 0
		
	def run_tick(self, dt):
		# run each of the warlocks simulations
		for user in self.usersData:
			if not user.warlock.dead:
				user.warlock.update(dt, self.bulletworld, self.spell_man, self.worldNP, self.usersData)
			# inside here the casting of spells happens, then once the spell manager takes control of the spell the rest will happen from it after this step
		
		# run the spells
		self.spell_man.update(dt, self.usersData, self.bulletworld)
		
		# run physics (just updates the collisionNP's i think so collision detections can work)
		self.bulletworld.doPhysics(dt, 1)
		
		self.ticks += 1
		
		# raise the lava
		self.world.raise_lava()
		
		return True
