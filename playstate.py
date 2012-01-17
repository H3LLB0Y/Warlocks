"""
Mouse move to edge of screen moves camera
Also arrow keys do
Middle mouse button and move mouse rotates the camera around the model
C centers camera on the warlock
Right click gives destination for warlock
"""

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

game_tick=1.0/60.0

class Playstate():
	# Initialisation Function
	def __init__(self,showbase):
		# Initialise Window
		self.showbase=showbase
		
		# total time since start of game, to keep ticks updating on time (rather, not before)
		self.total_time = 0
		
		# packets queue
		self.incoming=deque()
		
		# this is unnecessary lol but meh ill comment it anyway
		self.title = OnscreenText(text = "Angle: "+str(0.0), pos = (0.95,-0.95), 
											scale = 0.07,fg=(1,1,1,1),align=TextNode.ACenter,mayChange=1)
		
		# Keys array (down if 1, up if 0)
		self.keys={"left":0,"right":0,"up":0,"down":0,"c":0,"x":0}
		
		self.skybox=Skybox(self.showbase)
		
		self.ch=CameraHandler()
		
		self.game=Game(self.showbase.num_warlocks,game_tick,self.showbase)
		
		self.warlock=self.game.warlock[self.showbase.which]

		self.tick=0
		self.temp_tick=0
		
		# Set event handlers for keys		
		self.showbase.accept("escape",sys.exit)
		# holding c will focus the camera on clients warlock
		self.showbase.accept("c",set_value,[self.keys,"c",1])
		self.showbase.accept("c-up",set_value,[self.keys,"c",0])
		
		# variable to track which spell has been requested
		self.current_spell=0
		
		# keys to change spell
		self.showbase.accept("q",self.set_spell,[1])
		self.showbase.accept("w",self.set_spell,[2])
		self.showbase.accept("e",self.set_spell,[3])
		self.showbase.accept("r",self.set_spell,[4])
		
		# mouse 1 is for casting the spell set by the keys
		self.showbase.accept("mouse1",self.cast_spell)
		
		# mouse 3 is for movement, or canceling keys for casting spell
		self.showbase.accept("mouse3",self.update_destination)
		
		# Create a method to read key-status and then do. on server side.
		# Should add a key here for the spell.. .
		# x is for spell test.
		self.showbase.accept("x",set_value,[self.keys,"spell1", 1])
		self.showbase.accept("x-up",set_value,[self.keys,"spell1", 0])
		#self.showbase.accept("a",self.warlock.add_spell_vel,[Vec3(20,0,0)])
		#self.showbase.accept("d",self.warlock.add_spell_vel,[Vec3(-20,0,0)])
		#self.showbase.accept("w",self.warlock.add_spell_vel,[Vec3(0,-20,0)])
		#self.showbase.accept("s",self.warlock.add_spell_vel,[Vec3(0,20,0)])
		#self.showbase.accept("+",self.warlock.add_damage,[1])
		#self.showbase.accept("-",self.warlock.add_damage,[-1])
		
		self.update_camera(0)
		
		# Add the game loop procedure to the task manager.
		self.showbase.taskMgr.add(self.game_loop,"Game Loop")
		
	def set_spell(self,spell):
		self.current_spell=spell
		
	def cast_spell(self):
		if not self.current_spell==0:
			data = {}
			data[0] = "spell"
			data[1] = self.current_spell
			self.showbase.client.sendData(data)
			self.current_spell=0
		
	def update_destination(self):
		print "update_destination "+str(self.current_spell)
		if self.current_spell==0:
			destination=self.ch.get_mouse_3d()
			if not destination.getZ()==-1:
				data = {}
				data[0] = "destination"
				data[1] = {}
				data[1][0] = destination.getX()
				data[1][1] = destination.getY()
				self.showbase.client.sendData(data)
		else:
			self.current_spell=0

	def update_camera(self,dt):
		# sets the camMoveTask to be run every frame
		self.ch.camMoveTask(dt)
		
		# if c is down update camera to always be following on the warlock
		if self.keys["c"]:
			follow=self.warlock
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
				if package[1]==0:
					self.total_time=0
				# check what tick it should be
				self.temp_tick=package[1]
				# if this tick needs to be run (if frames are up to the server tick)
				if self.temp_tick*game_tick<=self.total_time:
					# run tick
					self.game.run_tick()
					self.update_camera(game_tick)
					#self.tick+=1
					valid_packet=True
				else:
					#print "temp: "+str(self.temp_tick*game_tick)
					#print "total:"+str(self.total_time)
					# otherwise put packet back on front of list and end frame processing
					self.incoming.appendleft(package)
					break
			elif package[0]=='update':
				# if its an update packet then update destination of required warlock
				print "Update: "+str(package[1])+" "+str(package[2])
				self.game.warlock[package[1]].set_destination(Vec3(package[2][0],package[2][1],0))
				valid_packet=True
			if not valid_packet:
				data = {}
				data[0] = "error"
				data[1] = "Fail Server"
				self.game.client.sendData(data)
				print "Bad packet from server"
				print "Received: " + str(package)
			
		# Return cont to run task again next frame
		return task.cont
