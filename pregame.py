from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

from spell							import Spell
from spellmanager					import SpellManager

# This should get a new name something like pregame, or the codes should move.
class Pregame():
	def __init__(self, showbase):
		# prior to actually moving to this state a 'loading' state will happen
		# receiving the spells data from server and player data and shit
		self.showbase=showbase
		
		self.ready=False
		
		# this will have its own chat i guess, just game server only (no channels or anything just the one chat, all to all)
		# also i guess all the players data (usernames, maybe others) will need to be collected here from the server for the chat/scoreboard/whatever
		# and whenever a new person joins/leaves an update will be sent to all the clients (like with the all chat i guess)
		# these will need to be created in here from data passed from the server (where it will be procedurally generated)
		
		# once it receives a 'preround' state change it should create all the required shit (warlocks per person and the Game() class and whatnot)
		# then client will switch to preround state
		
		self.background = OnscreenImage(
			image  = 'media/gui/lobby/lobby.png',
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
			command   = showbase.quit,
			frameSize = (-4,-1,0,0),#-3, 3, -.5, 1),
			pos       = (-1.0, 0.0, -1.0),
			scale     = .1,
			text      = "QUIT!",
		)
		
		# Add the game loop procedure to the task manager.
		taskMgr.doMethodLater(1.0, self.update_lobby, 'Update Lobby')
		
	def update_lobby(self, task):
		temp=self.showbase.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package)
					if package[0]=='auth':
						# if authenticated then receive all the spells and warlocks
						print 'Authenticated YEAH!!!'
					# if username is sent, assign to client
					elif package[0]=='chat':
						print "Chat: "+self.showbase.clients[package[1][0]]+' said: '+package[1][1]
					elif package[0]=='spell':
						spell=Spell()
						spell.receive(package[1])
						self.showbase.spells.append(spell)
					elif package[0]=='client':
						self.showbase.clients[package[1][0]]=package[1][1]
						self.showbase.num_warlocks+=1
						print 'client '+str(package[1][0])+' '+str(package[1][1])
					elif package[0]=='which':
						self.showbase.which=package[1]
						print "i am warlock: "+str(package[1])
					# changes to game state (i guess this could be done the same as the gamestate ones, all but this change state packet, which will be same
					elif package[0]=='state':
						print "state: "+package[1]
						if package[1]=='preround':
							self.showbase.start_preround()
							return task.done
				else:
					print "Packet wrong size"
			
		return task.again
	
	def toggle_ready(self):
		self.ready=True
		data = {}
		data[0] = "ready"
		data[1] = "ready"
		self.ready_button.hide()
		self.unready_button.show()
		self.showbase.client.sendData(data)
		
	def toggle_unready(self):
		self.unready=True
		data = {}
		data[0] = "unready"
		data[1] = "unready"
		self.unready_button.hide()
		self.ready_button.show()
		self.showbase.client.sendData(data)
	
	def send_message(self):
		data = {}
		data[0] = "chat"
		data[1] = self.entry.get()
		self.entry.enterText('')
		self.showbase.client.sendData(data)

	def clearText(self):
		self.entry.enterText('')

	def hide(self):
		self.background.hide()
		
		self.send_button.hide()
		self.entry.hide()
		self.ready_button.hide()
		self.unready_button.hide()
		self.quit_button.hide()
