from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""    
	window-title WARLOCKS LOGIN
	fullscreen 0
	win-size 1024 768
	cursor-hidden 0
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText  import OnscreenText

from pandac.PandaModules      import *
import sys

from client							import Client

from prelobby import PreLobby
from mainmenu import MainMenu
from lobby import Lobby
from pregame import Pregame
from playstate import Playstate

class Main(ShowBase, DirectObject):
	def __init__(self):
		self.created_client=False
		ShowBase.__init__(self)
		self.prelobby=PreLobby(self)
	
	def login(self,username,password):
		self.username=username
		self.status=OnscreenText(text = "Attempting to login...", pos = Vec3(0, -0.4, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter)
		# simulate authentication by delaying before continuing
		# if authentication fails, create prelobby again with status text "LOGIN FAILED!"
		#self.prelobby=PreLobby(self,"LOGIN FAILED!")
		# else proceed to lobby state
		taskMgr.doMethodLater(0.01, self.start_mainmenu, 'Start MainMenu')
		
	def start_mainmenu(self,task):
		self.prelobby.destroy()
		self.status.destroy()
		self.mainmenu=MainMenu(self)
		return task.done
		
	def join_server(self,address):
		# Connect to our server
		self.client = Client(address, 9099, compress=True)
		if self.client.getConnected():
			self.created_client=True
			data = {}
			data[0]="username"
			data[1]=self.username
			self.client.sendData(data)
			taskMgr.doMethodLater(0.01, self.start_lobby, 'Start Lobby')
			return True
		else:
			return False
		
	def start_lobby(self,task):
		self.mainmenu.hide()
		self.status.destroy()
		self.lobby=Lobby(self)
		return task.done
		
	def join_game(self):
		print "Game Starting"
		taskMgr.doMethodLater(0.01, self.start_game, 'Start Game')
	
	def start_game(self,task):
		self.lobby.hide()
		self.status.destroy()
		self.pregame=Pregame(self)
		return task.done
		
	def begin_round(self):
		print "Game Starting"
		taskMgr.doMethodLater(0.01, self.start_round, 'Start Round')
	
	def start_round(self,task):
		#self.pregame.hide()
		#self.status.destroy()
		self.playstate=Playstate(self)
		return task.done
	
	def quit(self):
		sys.exit()

game = Main()
game.run()
