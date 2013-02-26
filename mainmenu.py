from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

from client							import Client

class MainMenu():
	def __init__(self, showbase):
		self.showbase = showbase
		
		self.status = OnscreenText(text = "", pos = Vec3(0, -0.35, 0), scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter, mayChange=True)
		
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

		self.ip = '127.0.0.1' # Should make this write to file... so that the user can save ip's...
		# yep thats a good idea, there will be a few things i guess that need to be done like this
		# like settings and keys and whatnot
		
		# Buttons
		self.buttons = []
		serverButtons = Vec3(-0.60, 0, -0.79)
		# Host
		self.params = ['3', '8']
		p = serverButtons + Vec3(-0.25, 0, 0)
		self.hostButton = DirectButton(text = 'Host', pos = p,  scale = 0.048, relief = DGG.GROOVE, command = self.showbase.host_game, extraArgs = [self.params])
		self.buttons.append(self.hostButton)
		# Join
		p = serverButtons + Vec3(0.0, 0.0, 0.0)
		self.joinButton = DirectButton(text = 'Join', pos = p, scale = 0.048, relief = DGG.GROOVE, command = self.join_server)
		self.buttons.append(self.joinButton)
		# Refresh
		if self.showbase.online:
			p = serverButtons + Vec3(0.25, 0, 0)
			self.refreshButton = DirectButton(text = "Refresh", pos = p, scale = 0.048, relief = DGG.GROOVE, command = self.refresh_start)
			self.buttons.append(self.refreshButton)
			self.refresh_start()
			
			chatFrameCenter = (0.0, 0.325)
			chatFrameSize = (2.5, 1.2)
			self.chat = DirectFrame(
							frameColor = (0, 0, 0, 1),
							frameSize = (chatFrameSize[0] / 2, - chatFrameSize[0] / 2,  chatFrameSize[1] / 2, - chatFrameSize[1] / 2),
							pos = (chatFrameCenter[0], 0, chatFrameCenter[1])
						)
			
			channelFrameSize = (chatFrameSize[0] / 4, chatFrameSize[1])
			channelFrameCenter = (- chatFrameSize[0] / 2 + channelFrameSize[0] / 2, 0)
			numItemsVisible = 8
			itemHeight = channelFrameSize[1] / (numItemsVisible + 1)
			self.channels = DirectScrolledList(
								parent = self.chat,
								pos = (channelFrameCenter[0], 0, channelFrameCenter[1]),
								frameSize = (- channelFrameSize[0] / 2, channelFrameSize[0] / 2, channelFrameSize[1] / 2, - channelFrameSize[1] / 2),
								frameColor = (1, 0, 0, 0.5),
								numItemsVisible = numItemsVisible,
								forceHeight = itemHeight,

								#itemFrame_frameSize = (- channelFrameSize[0] / 2.1, channelFrameSize[0] / 2.1, itemHeight, - channelFrameSize[1] + itemHeight),
								itemFrame_pos = (0, 0, channelFrameSize[1] / 2 - itemHeight),

								decButton_pos = (-0.2, 0, channelFrameCenter[1] - channelFrameSize[1] / 2 + itemHeight / 4),
								decButton_text = 'Prev',
								decButton_text_scale = 0.05,
								decButton_borderWidth = (0.005, 0.005),

								incButton_pos = (0.2, 0, channelFrameCenter[1] - channelFrameSize[1] / 2 + itemHeight / 4),
								incButton_text = 'Next',
								incButton_text_scale = 0.05,
								incButton_borderWidth = (0.005, 0.005),
							)

			b1 = DirectButton(text = ("Button1", "click!", "roll", "disabled"),
								text_scale = 0.1, borderWidth = (0.01, 0.01),
								relief = 2)
			 
			b2 = DirectButton(text = ("Button2", "click!", "roll", "disabled"),
								text_scale = 0.1, borderWidth = (0.01, 0.01),
								relief = 2)
			
			l1 = DirectLabel(text = "Test1", text_scale = 0.1)
			l2 = DirectLabel(text = "Test2", text_scale = 0.1)
			l3 = DirectLabel(text = "Test3", text_scale = 0.1)

			self.channels.addItem(b1)
			self.channels.addItem(b2)
			self.channels.addItem(l1)
			self.channels.addItem(l2)
			self.channels.addItem(l3)

			for fruit in ['apple', 'pear', 'banana', 'orange', 'cake', 'chocolate']:
				l = DirectLabel(text = fruit, text_scale = 0.1)
				self.channels.addItem(l) 
			# need to add the chat stuff
			# i guess have like a chat manager which will hold an array of 'chat_instances'
			# and the chat manager can sort out which is displayed and which channel the text is sent from/received to
			# a bit more thinking needs to be done i guess
			# can discuss sometime (not really that important now :P)
			
			# also i guess the layout and shit will need to be sorted (for whoever is doing the designing)
			
			# current games list (need to implement this)
			# it should send a query to the master server to get the current list (just ip's atmo i guess)
			
			# options shit aswell needs to be sorted
			# maybe just an overlay or something
			
			# functionality for the host button (popup an overlay that will be able to set options and then 'start_game' button
			# then should auto connect and go to lobby (will be same as for all clients, except have a couple of different buttons i guess)
			# close game instead of disconnect, start game instead of ready (greyed until all others are ready), kick button i suppose
			
			# once the options are set the 'server_inst' should be started on the local computer (which will broadcast to master server, once host can successfully connect)
			# then game client will move to pregame state (connect to the server, and wait for others and ready)
		else:
			self.entry = DirectEntry(
							command = self.setIp,
							focusInCommand = self.clearText,
							frameSize   = (-3, 3, -.5, 1),
							initialText = self.ip,
							parent      = self.buttons[0],
							pos         = (0, -0.6, -1.5),
							text_align  = TextNode.ACenter,
						)

	def refresh_start(self):
		self.refreshButton["state"] = DGG.DISABLED
		if self.showbase.auth_con.getConnected():
			self.servers = []
			self.showbase.auth_con.sendData('server_query')
			taskMgr.doMethodLater(0.25, self.query_servers, 'Server Query')

	def query_servers(self, task):
		finished = False
		temp = self.showbase.auth_con.getData()
		for package in temp:
			if len(package) == 2:
				# Handle Server Query
				if package[0] == 'server':
					self.servers.append(package[1])
					print package[1]
				elif package[0] == 'final':
					self.refreshButton["state"] = DGG.NORMAL
					finished = True
				else:
					self.showbase.auth_con.passData(package)
		if finished:
			return task.done
		return task.cont

	def join_chat(self):
		pass
		# Let the client mini auth with the lobby server(lobby_loop) by "Logging into the chat"
		# Since everything will be in the main menu? like a main chat window.. something similar to HoN i guess?
		# When the player opens the Join game by button, a list will be send from the lobby server telling it what games are active.
		# Then the player picks one and it connects via the host name/ip or whatever.
		# While this is busy happening the client stays connected to the lobby server.
		
	def join_server(self):
		self.status.setText('Attempting to join server @ ' + self.ip + '...')
		# attempt to connect to the game server
		self.showbase.client = Client(self.ip, 9099, compress = True)
		if self.showbase.client.getConnected():
			print 'Connected to server, Awaiting authentication...'
			self.showbase.client.sendData(('username', self.showbase.username))
			taskMgr.add(self.authorization_listener, 'Authorization Listener')
		else:
			self.status.setText('Could not Connect...')

	def authorization_listener(self, task):
		temp = self.showbase.client.getData()
		auth = False
		if temp != []:
			for package in temp:
				if len(package) == 2:
					if package[0] == 'auth':
						print 'Authentication Successful'
						auth = True
					elif package[0] == 'fail':
						self.status.setText('Authentication failed on server...')
						return task.done
					else:
						self.showbase.client.passData(package)
		if auth:
			self.showbase.start_pregame()
			return task.done
		return task.again

	def clearText(self):
		self.entry.enterText('')

	def hide(self):
		taskMgr.remove('Server Query Timeout')
		self.background.destroy()
		for b in self.buttons:
			b.destroy()
		self.status.destroy()
		if self.showbase.online:
			self.chat.destroy()
			self.channels.destroy()
		else:
			self.entry.destroy()

	def setIp(self, ip):
		self.ip = ip
