from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenText import OnscreenText
import sys, random
from pandac.PandaModules import CollisionTraverser, CollisionHandlerEvent, WindowProperties
from pandac.PandaModules import *
from direct.gui.DirectGui import *
from panda3d.core import TextNode
from direct.showbase.DirectObject import DirectObject

class Preround():
	# Initialisation Function
	def __init__(self,showbase):
		# Initialise Window
		#self.showbase=showbase
		showbase.begin_round()
		
		# Add the game loop procedure to the task manager.
		#taskMgr.doMethodLater(0.5, self.pregame_loop,"Pregame Loop")
		
	# Game Loop Procedure
	def pregame_loop(self,task):
		
		# Return cont to run task again next frame
		return task.again
	
	def printTask(self, task):
		# Print results
		print "Received: " + str(self.showbase.client.getData())
		print "Connected: " + str(self.showbase.client.getConnected())

		# Setup data to send to the server
		data = {}
		data["test"] = "test"

		# Send data to the server
		self.showbase.client.sendData(data)

		return Task.again
