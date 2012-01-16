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
from pandac.PandaModules import CollisionTraverser, CollisionHandlerEvent, WindowProperties
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from direct.showbase.DirectObject import DirectObject
from collections import deque

from CameraHandler				import CameraHandler
from warlock						import Warlock
from world							import World
from skybox							import Skybox
from util							import *

game_tick=1.0/60.0

#This function, given a line (vector plus origin point) and a desired z value,
#will give us the point on the line where the desired z value is what we want.
#This is how we know where to position an object in 3D space based on a 2D mouse
#position. It also assumes that we are dragging in the XY plane.
#
#This is derived from the mathmatical of a plane, solved for a given point
def PointAtZ(z, point, vec):
  return point + vec * ((z-point.getZ()) / vec.getZ())
# STOLEN FROM CHESSBOARD EXAMPLE

class Playstate():
	# Initialisation Function
	def __init__(self,game):
		# Initialise Window
		self.game=game
		
		# total time since start of game, to keep ticks updating on time
		self.total_time = 0
		
		# packets queue
		self.incoming=deque()
		
		# this is unnecessary lol but meh ill comment it anyway
		self.title = OnscreenText(text = "Angle: "+str(0.0), pos = (0.95,-0.95), 
											scale = 0.07,fg=(1,1,1,1),align=TextNode.ACenter,mayChange=1)
		
		# Keys array (down if 1, up if 0)
		self.keys={"left":0,"right":0,"up":0,"down":0,"c":0,"x":0}
		
		# Initialize the collision traverser.
		#base.cTrav = CollisionTraverser()
		
		# Initialize the handler.
		#self.collHandEvent = CollisionHandlerEvent()
		#self.collHandEvent.addInPattern('into-%in')
		
		# CHESSBOARD STUFF FOR PICKING POINT IN 3D SPACE FROM MOUSE CLICK
		#Since we are using collision detection to do picking, we set it up like
		#any other collision detection system with a traverser and a handler
		self.picker = CollisionTraverser()            #Make a traverser
		self.pq     = CollisionHandlerQueue()         #Make a handler
		#Make a collision node for our picker ray
		self.pickerNode = CollisionNode('mouseRay')
		#Attach that node to the camera since the ray will need to be positioned
		#relative to it
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		#Everything to be picked will use bit 1. This way if we were doing other
		#collision we could seperate it
		self.pickerNode.setFromCollideMask(BitMask32.bit(1))
		self.pickerRay = CollisionRay()               #Make our ray
		self.pickerNode.addSolid(self.pickerRay)      #Add it to the collision node
		#Register the ray as something that can cause collisions
		self.picker.addCollider(self.pickerNP, self.pq)
		#self.picker.showCollisions(render)
		# UNTIL HERE
		
		self.skybox=Skybox(self.game)
		
		self.ch=CameraHandler()
		
		self.warlock={}
		for i in range(self.game.num_warlocks):
			self.warlock[i]=Warlock(self.game,i)
		
		self.world=World(self.game)
		# Temp
		print self.warlock

		self.tick=0
		self.temp_tick=0
		
		# Create Ambient Light
		"""ambientLight = AmbientLight('ambientLight')
		ambientLight.setColor(Vec4(0.5,0.5,0.5,1))
		ambientLightNP = render.attachNewNode(ambientLight)
		render.setLight(ambientLightNP)
		
		# Directional light 02
		directionalLight = DirectionalLight('directionalLight')
		directionalLight.setColor(Vec4(0.9, 0.9, 0.9, 1))
		directionalLightNP = render.attachNewNode(directionalLight)
		# This light is facing forwards, away from the camera.
		directionalLightNP.setPos(0,10,10)
		directionalLightNP.lookAt(self.warlock) #setHpr(0,20,0)
		render.setLight(directionalLightNP)"""
		
		# Set event handlers for keys		
		self.game.accept("escape",sys.exit)
		# Using WASD Keys
		self.game.accept("a",set_value,[self.keys,"left",1])
		self.game.accept("d",set_value,[self.keys,"right",1])
		self.game.accept("w",set_value,[self.keys,"up",1])
		self.game.accept("s",set_value,[self.keys,"down",1])
		self.game.accept("a-up",set_value,[self.keys,"left",0])
		self.game.accept("d-up",set_value,[self.keys,"right",0])
		self.game.accept("w-up",set_value,[self.keys,"up",0])
		self.game.accept("s-up",set_value,[self.keys,"down",0])
		self.game.accept("c",set_value,[self.keys,"c",1])
		self.game.accept("c-up",set_value,[self.keys,"c",0])
		self.game.accept("mouse3",self.update_destination)
		
        # Create a method to read key-status and then do. on server side.
		# Should add a key here for the spell.. .
		# x is for spell test.
		self.game.accept("x",set_value,[self.keys,"spell1", 1])
		self.game.accept("x-up",set_value,[self.keys,"spell1", 0])
		#self.game.accept("a",self.warlock[0].add_spell_vel,[Vec3(20,0,0)])
		self.game.accept("d",self.warlock[0].add_spell_vel,[Vec3(-20,0,0)])
		self.game.accept("w",self.warlock[0].add_spell_vel,[Vec3(0,-20,0)])
		self.game.accept("s",self.warlock[0].add_spell_vel,[Vec3(0,20,0)])
		self.game.accept("+",self.warlock[0].add_damage,[1])
		self.game.accept("-",self.warlock[0].add_damage,[-1])
		
		self.game.accept("p",self.print_warlocks)
		
		# Add the game loop procedure to the task manager.
		self.game.taskMgr.add(self.game_loop,"Game Loop")

	def print_warlocks(self):
		for i in range(self.game.num_warlocks):
			print self.warlock[i].getPos()
		
	def update_destination(self):
		#Set the position of the ray based on the mouse position
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
			
			nearPoint = render.getRelativePoint(camera, self.pickerRay.getOrigin())
			#Same thing with the direction of the ray
			nearVec = render.getRelativeVector(camera, self.pickerRay.getDirection())
			#self.warlock[0].set_destination(PointAtZ(0, nearPoint, nearVec))
			destination=PointAtZ(0, nearPoint, nearVec)
			data = {}
			data[0] = "destination"
			data[1] = {}
			data[1][0] = destination.getX()
			data[1][1] = destination.getY()
			self.game.client.sendData(data)
			

	def run_tick(self,dt):
		
		self.ch.camMoveTask(dt)
		# sets the camMoveTask to be run every frame
		
		# here implement some kind of sliding phyiscs based on damage taken already
		# so heaps of damage means they keep sliding longer less friction
		for i in range(self.game.num_warlocks):
			self.warlock[i].update(dt)
		
		# if c is down update camera to always be following on the warlock
		follow=self.warlock[self.game.which]
		#if self.keys["c"]:
		self.ch.setTarget(follow.getPos().getX(),follow.getPos().getY(),follow.getPos().getZ())
		self.ch.turnCameraAroundPoint(0,0)
		
	# Game Loop Procedure
	def game_loop(self,task):
		# update total time
		self.total_time+=globalClock.getDt()
		# process any incoming network packets
		temp=self.game.client.getData()
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
					#print self.temp_tick
					self.run_tick(game_tick)
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
				self.warlock[package[1]].set_destination(Vec3(package[2][0],package[2][1],0))
				valid_packet=True
			if not valid_packet:
				data = {}
				data[0] = "error"
				data[1] = "Fail Server"
				self.game.client.sendData(data)
				print "Bad packet from server"
				print "Received: " + str(package)
			
		#if not self.tick==self.temp_tick:
		#	self.run_tick(game_tick)
			
		# Return cont to run task again next frame
		return task.cont
