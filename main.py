from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""    
	window-title WARLOCKS
	fullscreen 0
	win-size 1024 768
	cursor-hidden 0
	sync-video 1
	frame-rate-meter-update-interval 0.5
	show-frame-rate-meter 1
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText  import OnscreenText

from pandac.PandaModules      import *
import sys

from client							import Client

from login import Login
from mainmenu import MainMenu
from pregame import Pregame
from preround import Preround
from round import Round
from client_config import *


class Main(ShowBase):
	def __init__(self):
		self.created_client=False
		ShowBase.__init__(self)
		self.login=Login(self)
		self.client = Client(LOGIN_IP, LOGIN_PORT, compress=True)
		if not self.client.getConnected():
			self.login.updateStatus("Could not connect to the Login server")
			self.client=False
		
	def attempt_login(self, username, password):
		# check if processing a request already so if multiple presses of button it wont break this lol...
		# set a variable in login_packetReader() and check here
		
		# attempt to connect again if it failed on startup
		if not self.client:
			self.client = Client(LOGIN_IP, LOGIN_PORT, compress=True)
		if self.client.getConnected():
			self.username=username
			# Setup the un/up sendpacket, this will be changed. later :P
			data = {}
			data[0] = 'login_request'
			data[1] = {}
			data[1][0] = username
			data[1][1] = password
			self.client.sendData(data)
			# Add the handler for the login stage.
			taskMgr.doMethodLater(0.2, self.login_packetReader, 'Update Login')
			return True
		else:
			# client not connected to login/auth server so display message
			self.login.updateStatus("Could not connect to the Login server")
			self.client=False
	
	def create_account(self, username, password):
		# should be similar to attempt_login() but sends 'create_request' rather than 'login_request'
		# similarly need a create_packetReader() task to check for account_created success packet
		# then automatically call attempt_login with the username and password
		pass
	
	def login_packetReader(self, task):
		# setup some sort of timeout checker which will unset the checker variable in attempt_login function so it can go again
		# i think also for the 'db_reply' instead use the hex codes like you were thinking, and have each seperate code like 'already logged' 'wrong password/username' 'whatever else'
		# so on a return of a failure aswell, it will need to stop this task (return task.done)
		temp=self.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package)
					print "Connected to login server"
					# updates warlocks in game
					"""if package[0]=='error':
						print package
						print "User already logged"
						self.login.updateStatus(package[1])
						valid_packet=True
						break"""
					if package[0]=='db_reply':
						print "DB: "+str(package[1])
						self.login.updateStatus(package[1])
						valid_packet=True
					elif package[0]=='login_valid':
						print "Login valid: "+str(package[1])
						self.login.updateStatus(package[1][0])
						print "success: "+str(package[1][1])
						valid_packet=True
						print "I should move to main menu now..."
						taskMgr.doMethodLater(0.3, self.start_mainmenu, 'Start Main Menu')
						return task.done
					"""if not valid_packet:
						data = {}
						data[0] = "error"
						data[1] = "Fail Server"
						self.client.sendData(data)
						print "Bad packet from server"""
				else:
					print "Packet wrong size"
		return task.again
	
	def start_mainmenu(self,task):
		self.login.destroy()
		self.mainmenu=MainMenu(self)
		return task.done
		
	def join_server(self,address):
		# Store connection to lobby and chat i guess eventually
		self.lobby_con=self.client
		# attempt to connect to the game server
		self.client = Client(address, 9099, compress=True)
		if self.client.getConnected():
			print "Connected to server"
			data = {}
			data[0]="username"
			data[1]=self.username # This will end up being the selected server?
			self.client.sendData(data)
			taskMgr.doMethodLater(0.03, self.start_pregame, 'Start Pregame') # I guess this should change to Pregame.
			return True
		else:
			return False
		
	def start_pregame(self,task):
		self.mainmenu.hide()
		self.pregame=Pregame(self)
		return task.done
		
	def begin_preround(self):
		print "Game Starting"
		taskMgr.doMethodLater(0.01, self.start_preround, 'Start Preround')
	
	def start_preround(self,task):
		self.pregame.hide()
		self.preround=Preround(self)
		return task.done
		
	def begin_round(self):
		print "Round Starting"
		taskMgr.doMethodLater(0.01, self.start_round, 'Start Round')
	
	def start_round(self,task):
		self.preround.hide()
		self.round=Round(self)
		return task.done
	
	def quit(self):
		sys.exit()

game = Main()
game.run()
