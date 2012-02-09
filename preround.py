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
		self.showbase=showbase
		
		# Add the game loop procedure to the task manager.
		taskMgr.doMethodLater(2.5, self.pregame_loop,"Pregame Loop")
		
	# Game Loop Procedure
	def pregame_loop(self,task):
		self.showbase.begin_round()
		return task.done
		
		# needs to check for a 'tick' like packet that will signal to go to the round stage
		
		# Return cont to run task again next frame
		return task.again

	def hide(self):
		# hide whatever is created for this (icons and shit for spells) selection buttons w/e else
		pass
