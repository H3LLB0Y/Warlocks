from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	window-title WARLOCK [ARENA]
	fullscreen 0
	win-size 1024 768
	cursor-hidden 0
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

# For Showbase (main class)
from direct.showbase.ShowBase import ShowBase

# For Login state
from login import Login
# For MainMenu state
from mainmenu import MainMenu
# For Pregame state
from pregame import Pregame
# For Preround state
from preround import Preround
# For Round state
from round import Round

# For starting the server from within the game
from subprocess import *
# For exit function
import sys

class Main(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		self.login = Login(self)
	
	def start_mainmenu(self, prev):
		prev.hide()
		self.mainmenu = MainMenu(self)
	
	def start_pregame(self):
		self.mainmenu.hide()
		self.pregame = Pregame(self)
	
	def start_preround(self):
		self.pregame.hide()
		self.preround = Preround(self)
	
	def start_round(self):
		self.preround.hide()
		self.round = Round(self)
		
	def host_game(self, params):
		pid = Popen(["python", "server.py", params]).pid
	
	def quit(self):
		sys.exit()

game = Main()
game.run()
