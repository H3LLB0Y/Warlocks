from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

class Lobby():
	def __init__(self, game):
		self.game=game
		
		self.ready=False
		
		self.game.num_warlocks=1
		self.game.which=0
		
		self.background = OnscreenImage(
			image  = 'models/lobby.jpg',
			parent = render2d
		)
		
		# Send Message Button
		self.send_button = DirectButton(
			command   = self.send_message,
			frameSize = (-3, 3, -.5, 1),
			pos       = (0.0, 0.0, .3),
			scale     = .1,
			text      = "Send",
		)
		# Text box for message entry
		self.entry = DirectEntry(
			focusInCommand = self.clearText,
			frameSize   = (-3, 3, -.5, 1),
			initialText = "Chat:",
			parent      = self.send_button,
			pos         = (0, 0, -1.5),
			text        = "" ,
			text_align  = TextNode.ACenter,
		)
		# button to tell server client is ready
		self.ready_button = DirectButton(
			command   = self.toggle_ready,
			frameSize = (-3, 3, -.5, 1),
			pos       = (0.0, 0.0, -.3),
			scale     = .1,
			text      = "Ready?",
		)
		# button to tell server client is not ready
		self.unready_button = DirectButton(
			command   = self.toggle_unready,
			frameSize = (-3, 3, -.5, 1),
			pos       = (0.0, 0.0, -.3),
			scale     = .1,
			text      = "Unready?",
		)
		# hide unready button until ready
		self.unready_button.hide()
		
		# button to quit game
		self.quit_button = DirectButton(
			command   = game.quit,
			frameSize = (-4,-1,0,0),#-3, 3, -.5, 1),
			pos       = (-1.0, 0.0, -1.0),
			scale     = .1,
			text      = "QUIT!",
		)
		
		# Add the game loop procedure to the task manager.
		taskMgr.doMethodLater(1.0, self.update_lobby, 'Update Lobby')
		
	def update_lobby(self, task):
		temp=self.game.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package)
					# if username is sent, assign to client
					if package[0]=='chat':
						print "Chat: "+package[1]
						valid_packet=True
					# updates warlocks in game
					elif package[0]=='warlocks':
						print "warlocks: "+str(package[1])
						self.game.num_warlocks=package[1]
						valid_packet=True
					elif package[0]=='which':
						print "i am warlock: "+str(package[1])
						self.game.which=package[1]
						valid_packet=True
					# changes to game state
					elif package[0]=='state':
						print "state: "+package[1]
						if package[1]=='game':
							self.game.join_game()
						valid_packet=True
					if not valid_packet:
						data = {}
						data[0] = "error"
						data[1] = "Fail Server"
						self.game.client.sendData(data)
						print "Bad packet from server"
				else:
					print "Packet wrong size"
			
		return task.again
		
	#def select_spell(self,spell):
		
	
	def toggle_ready(self):
		self.ready=True
		data = {}
		data[0] = "ready"
		data[1] = "ready"
		self.ready_button.hide()
		self.unready_button.show()
		self.game.client.sendData(data)
		
	def toggle_unready(self):
		self.unready=True
		data = {}
		data[0] = "unready"
		data[1] = "unready"
		self.unready_button.hide()
		self.ready_button.show()
		self.game.client.sendData(data)
	
	def send_message(self):
		data = {}
		data[0] = "chat"
		data[1] = self.entry.get()
		self.entry.enterText('')
		self.game.client.sendData(data)

	def clearText(self):
		self.entry.enterText('')

	def hide(self):
		self.background.hide()
		
		self.send_button.hide()
		self.entry.hide()
		self.ready_button.hide()
		self.unready_button.hide()
		self.quit_button.hide()
