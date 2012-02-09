from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

class MainMenu():
	def __init__(self, game):
		self.game=game
		
		self.status=OnscreenText(text = "", pos = Vec3(0, -0.35, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter, mayChange=True)
		
		self.background = OnscreenImage(
			image  = 'media/gui/mainmenu/menu.png',
			parent = render2d
		)

		self.title = OnscreenText(
			text   = 'Main Menu',
			fg     = (1, 1, 1, 1),
			parent = self.background,
			pos    = (-0.6, 0.1),
			scale  = 0.06
		)

		self.ip = "127.0.0.1" # Should make this write to file... so that the user can save ip's...
		# yep thats a good idea, there will be a few things i guess that need to be done like this
		# like settings and keys and whatnot

		self.buttons = []
		# Buttons
		boxloc = Vec3(0.0, 0.0, 0.0)
		# Host
		p = boxloc + Vec3(-0.85, 0, -0.79)
		self.hostButton = DirectButton(text="Host", pos = p,  scale = 0.048, relief=DGG.GROOVE, command='')
		
		p = boxloc + Vec3(-0.65, 0, -0.79)
		self.joinButton = DirectButton(text="Join", pos=p, scale=0.048, relief=DGG.GROOVE, command=self.join_server)
		
		
		self.addButton("Join Server",  self.join_server,1, -.1)
		
		self.entry = DirectEntry(
			command = self.setIp,
			focusInCommand = self.clearText,
			frameSize   = (-3, 3, -.5, 1),
			initialText = self.ip,
			parent      = self.buttons[0],
			pos         = (0, -0.6, -1.5),
			text        = "" ,
			text_align  = TextNode.ACenter,
		)
		
		self.addButton("QUIT!",  game.quit,1, -.5)
		
		# need to add the chat stuff
		# i guess have like a chat manager which will hold an array of 'chat_instances'
		# and the chat manager can sort out which is displayed and which channel the text is sent from/received to
		# a bit more thinking needs to be done i guess
		# can discuss sometime (not really that important now :P)
		
		# also i guess the layout and shit will need to be sorted (for whoever is doing the designing)
		
		# current games list (need to implement this)
		# it should send a query to the master server to get the current list (just ip's atmo i guess)
		# query should be sent on __init__() i.e. here :P and when refresh button is pressed (maybe instead on auto time)
		# have a time limit on wait before new refresh is requested
		# setup a task to listen for games (on refresh and once received task.done it)
		# still something that needs to be decided on how it will work
		# when one is clicked on and selected it should be tracked so when the refresh happens it still is selected
		
		# options shit aswell needs to be sorted
		# maybe just an overlay or something
		
		# functionality for the host button (popup an overlay that will be able to set options and then 'start_game' button
		# then should auto connect and go to lobby (will be same as for all clients, except have a couple of different buttons i guess)
		# close game instead of disconnect, start game instead of ready (greyed until all others are ready), kick button i suppose
		
		# once the options are set the 'server_inst' should be started on the local computer (which will broadcast to master server, once host can successfully connect)
		# then game client will move to pregame state (connect to the server, and wait for others and ready)

	def join_chat(self):
		pass
		# Let the client mini auth with the lobby server(lobby_loop) by "Logging into the chat"
		# Since everything will be in the main menu? like a main chat window.. something similar to HoN i guess?
		# When the player opens the Join game by button, a list will be send from the lobby server telling it what games are active.
		# Then the player picks one and it connects via the host name/ip or whatever.
		# While this is busy happening the client stays connected to the lobby server.
		
	# Check here for the blocking.
	def join_server(self):
		self.setIp(self.entry.get())
		self.status.setText("Attempting to join server @ "+self.ip+"...")
		if self.game.join_server(self.ip):
			self.status.setText("")
		else:
			self.status.setText("Could not Connect...")

	def addButton(self, text, command,xPos, zPos):
		button = DirectButton(
			command   = command,
			frameSize = (-2, 2, -.3, 1),
			pos       = (xPos, 0.0, zPos),
			scale     = .1,
			text      = text,
		)

		self.buttons.append(button)

	def clearText(self):
		self.entry.enterText('')

	def hide(self):
		self.background.hide()
		for b in self.buttons:
			b.hide()

	def setIp(self, ip):
		print "set ip", ip
		self.ip = ip
