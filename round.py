from math import pi, sin, cos, atan2
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
import sys, random
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from direct.showbase.DirectObject import DirectObject
from collections import deque

from CameraHandler				import CameraHandler
from skybox							import Skybox
from util							import *
from game							import Game
from spellmanager					import SpellManager

game_tick=1.0/60.0

class Round():
	# Initialisation Function
	def __init__(self,showbase):
		# Initialise Window
		self.showbase=showbase
		
		# total time since start of game, to keep ticks updating on time (rather, not before)
		self.total_time = 0
		
		# packets queue
		self.incoming=deque()
		
		# this is unnecessary lol but meh ill comment it anyway
		self.hp = OnscreenText(text = "HP: "+str(100.0), pos = (0.95,-0.95), 
											scale = 0.07,fg=(1,1,1,1),align=TextNode.ACenter,mayChange=1)
		
		# Keys array (down if 1, up if 0)
		self.keys={"left":0,"right":0,"up":0,"down":0,"c":0,"x":0}
		
		self.skybox=Skybox(self.showbase)
		
		self.ch=CameraHandler()
		
		# maybe this shit too, or this can stay here and just pass in an array of spells 
		self.showbase.spell_man=SpellManager(self.showbase.num_warlocks) # until the Game() class is created in here which i think it should
		for i in self.showbase.spells:
			self.showbase.spell_man.add_spell(i)
		
		self.game=Game(self.showbase,game_tick)
			
		self.warlock=self.game.warlock[self.showbase.which]
		self.warlock.attach_ring(self.showbase)
		
		self.tick=0
		self.temp_tick=0
		
		# Set event handlers for keys		
		self.showbase.accept("escape",sys.exit)
		# holding c will focus the camera on clients warlock
		self.showbase.accept("c",set_value,[self.keys,"c",1])
		self.showbase.accept("c-up",set_value,[self.keys,"c",0])
		
		# variable to track which spell has been requested
		self.current_spell=-1
		
		# keys to change spell
		self.showbase.accept("q",self.set_spell,[0])
		self.showbase.accept("w",self.set_spell,[1])
		self.showbase.accept("e",self.set_spell,[2])
		self.showbase.accept("r",self.set_spell,[3])
		
		# mouse 1 is for casting the spell set by the keys
		self.showbase.accept("mouse1",self.cast_spell)
		
		# mouse 3 is for movement, or canceling keys for casting spell
		self.showbase.accept("mouse3",self.update_destination)
		
		# sets the camera up behind clients warlock looking down on it from angle
		follow=self.warlock.model
		self.ch.setTarget(follow.getPos().getX(),follow.getPos().getY(),follow.getPos().getZ())
		self.ch.turnCameraAroundPoint(follow.getH(),0)
		
		# Add the game loop procedure to the task manager.
		self.showbase.taskMgr.add(self.game_loop,"Game Loop")
		
	def set_spell(self,spell):
		self.current_spell=spell
	
	# sends spell request to server if one is selected
	def cast_spell(self):
		if not self.current_spell==-1:
			target=self.ch.get_mouse_3d()
			if not target.getZ()==-1:
				data = {}
				data[0] = "spell"
				data[1] = {}
				data[1][0] = self.current_spell
				data[1][1] = {}
				data[1][1][0] = target.getX()
				data[1][1][1] = target.getY()
				self.showbase.client.sendData(data)
				self.current_spell=-1
	
	# sends destination request to server, or cancels spell if selected
	def update_destination(self):
		if self.current_spell==-1:
			destination=self.ch.get_mouse_3d()
			if not destination.getZ()==-1:
				data = {}
				data[0] = "destination"
				data[1] = {}
				data[1][0] = destination.getX()
				data[1][1] = destination.getY()
				self.showbase.client.sendData(data)
		else:
			self.current_spell=-1

	def update_camera(self,dt):
		# sets the camMoveTask to be run every frame
		self.ch.camMoveTask(dt)
		
		# if c is down update camera to always be following on the warlock
		if self.keys["c"]:
			follow=self.warlock.model
			self.ch.setTarget(follow.getPos().getX(),follow.getPos().getY(),follow.getPos().getZ())
			self.ch.turnCameraAroundPoint(0,0)
		
	# Game Loop Procedure
	def game_loop(self,task):
		# update total time
		self.total_time+=globalClock.getDt()
		# process any incoming network packets
		temp=self.showbase.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				# this part puts the next packets onto the end of the queue
				self.incoming.append(temp[i])
		
		# while there is packets to process
		while list(self.incoming):
			valid_packet=False
			package=self.incoming.popleft()
			# if username is sent, assign to client
			if package[0]=='tick':
				# not sure if this is the best way to do this but yea something to look into for syncing them all preround i guess
				if package[1]==0:
					self.total_time=0
				# check what tick it should be
				self.temp_tick=package[1]
				# if this tick needs to be run (if frames are up to the server tick)
				if self.temp_tick*game_tick<=self.total_time:
					# run tick
					if not self.game.run_tick():
						print 'Game Over'
					self.update_camera(game_tick) # maybe this should be put outside of this loop and just updated from the globalClock.getDt()
					self.hp.setText("HP: "+str(self.warlock.hp)) # i think there should be a HUD class which will show all the info needed for the player (like hps,spells cds, etc)
					valid_packet=True
				else:
					# otherwise put packet back on front of list and end frame processing
					self.incoming.appendleft(package)
					break
			# i think it should check for 'tick' and if not tick then pass the rest of the packets to a packet handler (kind of makes it more modable i guess for changing the game to another like pudgewars or centipede or w/e)
			# so i guess these will be put into a packet manager (i think this idea you had before anyway :P) silly me! :D
			# well, just leave here for now i guess :P
			elif package[0]=='update_dest':
				# if its an update packet then update destination of required warlock
				print "Update Destination: "+str(package[1])+" "+str(package[2])
				self.game.warlock[package[1]].set_destination(Vec3(package[2][0],package[2][1],0))
				valid_packet=True
			elif package[0]=='update_spell':
				# if its an update packet then update destination of required warlock
				print "Update Spell: "+str(package[1])+" "+str(package[2])+" "+str(package[3])
				self.game.warlock[package[1]].set_spell(package[2],package[3])
				valid_packet=True
			
		# Return cont to run task again next frame
		return task.cont
