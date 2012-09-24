from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

import ConfigParser, os
from client						import Client

class Login():
	def __init__(self, showbase):
		self.showbase = showbase
		
		self.background = OnscreenImage(
			image  = 'media/gui/login/bg.png',
			parent = render2d
		)
		
		base.setBackgroundColor(0, 0, 0)
		# sets the background color to black because the
		# default grey color bugs me for some reason

		### CONFIG LOADER ###
		config = ConfigParser.RawConfigParser()
		config.read('master.cfg')
		self.LOGIN_IP = config.get('MASTER SERVER CONNECTION', 'master_ip')
		self.LOGIN_PORT = config.getint('MASTER SERVER CONNECTION', 'master_port')

		config = ConfigParser.RawConfigParser()
		config.read('client.cfg')
		self.store_username = config.getint('USERDATA', 'store_username')
		if self.store_username == 1:
			self.username = config.get('USERDATA', 'username')
		else:
			self.username = ''
		self.store_password = config.getint('USERDATA', 'store_password')
		if self.store_password == 1:
			self.password = config.get('USERDATA', 'password')
		else:
			self.password = ''
		### CONFIG END ###

		self.loginScreen("Press 'Enter' to login")
		# draws the login screen

		self.usernameBox['focus'] = 1
		# sets the cursor to the username field by default

		showbase.accept('tab', self.cycleLoginBox)
		showbase.accept('shift-tab', self.cycleLoginBox)
		# enables the user to cycle through the text fields with the tab key
		# this is a standard feature on most login forms

		showbase.accept('enter', self.attemptLogin)         
		# submits the login form, or you can just click the Login button
		
		# checking variable to stop multiple presses of the button spawn multiple tasks
		self.request_attempt = False
		
		self.showbase.client = Client(self.LOGIN_IP, self.LOGIN_PORT, compress = True)
		if not self.showbase.client.getConnected():
			self.updateStatus("Could not connect to the Login server")
			self.showbase.client = False

	def update_config(self):
		config = ConfigParser.RawConfigParser()
		config.read('client.cfg')
		config.set('USERDATA', 'store_username', self.usernameStoreBox["indicatorValue"])
		config.set('USERDATA', 'store_password', self.passwordStoreBox["indicatorValue"])
		if self.usernameStoreBox["indicatorValue"] == 1:
			config.set('USERDATA', 'username', self.usernameBox.get())
		if self.passwordStoreBox["indicatorValue"] == 1:
			config.set('USERDATA', 'password', self.passwordBox.get())
		with open('client.cfg', 'wb') as configfile:
			config.write(configfile)
	
	def loginScreen(self, statusText):
		# creates a basic login screen that asks for a username/password
		
		boxloc = Vec3(0.0, 0.0, 0.0)
		# all items in the login form will have a position relative to this
		# this makes it easier to shift the entire form around once we have
		# some graphics to display with it without having to change the
		# positioning of every form element

		# p is the position of the form element relative to the boxloc
		# coordinates set above it is changed for every form element
		p = boxloc + Vec3(-0.22, 0.09, 0.0)                                 
		self.usernameText = OnscreenText(text = "Username:", pos = p, scale = 0.05, bg = (0, 0, 0, 1), fg = (1, 1, 1, 1), align = TextNode.ARight)
		# "Username: " text that appears beside the username box

		p = boxloc + Vec3(-0.2, 0.0, 0.09)
		self.usernameBox = DirectEntry(text = "", pos = p, scale=.04, initialText = self.username, numLines = 1)
		# Username textbox where you type in your username
		
		p = boxloc + Vec3(0.4, 0.0, 0.09)
		self.usernameStoreBox = DirectCheckButton(text = "Save Username?", pos = p, scale = .04, indicatorValue = self.store_username)
		# Toggle to save/not save your username
		
		p = boxloc + Vec3(-0.22, 0.0, 0.0)       
		self.passwordText = OnscreenText(text = "Password:", pos = p, scale = 0.05, bg = (0,0,0,1), fg = (1, 1, 1, 1), align = TextNode.ARight)
		# "Password: " text that appears beside the password box

		p = boxloc + Vec3(-0.2, 0.0, 0.0)
		self.passwordBox = DirectEntry(text = "", pos = p, scale = .04, initialText = self.password, numLines = 1, obscured = 1)
		# Password textbox where you type in your password
		# Note - obscured = 1 denotes that all text entered will be replaced
		# with a * like a standard password box
		
		p = boxloc + Vec3(0.4, 0.0, 0.0)
		self.passwordStoreBox = DirectCheckButton(text = "Save Password?", pos = p, scale = .04, indicatorValue = self.store_password)
		# Toggle to save/not save your username
		
		p = boxloc + Vec3(0, 0, -0.090)
		self.loginButton = DirectButton(text = "Login", pos = p, scale = 0.048, relief = DGG.GROOVE, command = self.attemptLogin)
		# The 'Quit' button that will trigger the Quit function
		# when clicked
		
		p = boxloc + Vec3(0.95, 0, -0.9)
		self.createAccButton = DirectButton(text = "Create Account", scale = 0.050, pos = p, relief = DGG.GROOVE, command = self.attemptCreateAccount)
		# Made a quick button for adding accounts. Its fugly

		p = boxloc + Vec3(1.20, 0, -0.9)
		self.quitButton = DirectButton(text = "Quit", pos = p, scale = 0.048, relief = DGG.GROOVE, command = self.showbase.quit)
		# The 'Quit' button that will trigger the Quit function
		# when clicked
		
		p = boxloc + Vec3(0, -0.4, 0)
		self.statusText = OnscreenText(text = statusText, pos = p, scale = 0.043, fg = (1, 0.5, 0, 1), align = TextNode.ACenter)
		# A simple text object that you can display an error/status messages
		# to the user

	def updateStatus(self, statusText):
		self.statusText.setText(statusText)
		# all this does is change the status text.

	def checkBoxes(self):
		# checks to make sure the user inputed a username and password:
		#       if they didn't it will spit out an error message
		self.updateStatus("")
		if self.usernameBox.get() == "":
			if self.passwordBox.get() == "":
				self.updateStatus("You must enter a username and password before logging in.")
			else:
				self.updateStatus("You must specify a username")
				self.passwordBox['focus'] = 0
				self.usernameBox['focus'] = 1
			return False
		elif self.passwordBox.get() == "":
			self.updateStatus("You must enter a password")
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1
			return False
		# if both boxes are filled then return True
		return True

	def attemptLogin(self):
		if self.checkBoxes():
			self.showbase.username = self.usernameBox.get()
			self.updateStatus("Attempting to login...")
			self.request(self.usernameBox.get(), self.passwordBox.get(), 'client')
			
	def attemptCreateAccount(self):
		if self.checkBoxes():
			self.updateStatus("Attempting to create account and login...")
			self.request(self.usernameBox.get(), self.passwordBox.get(), 'create')
	
	def request(self, username, password, request):
		if not self.request_attempt:
			# attempt to connect again if it failed on startup
			if not self.showbase.client:
				self.showbase.client = Client(self.LOGIN_IP, self.LOGIN_PORT, compress = True)
			if self.showbase.client.getConnected():
				self.request_attempt = True
				self.loginButton["state"] = DGG.DISABLED
				self.createAccButton["state"] = DGG.DISABLED
				self.showbase.client.sendData((request, (username, password)))
				# Add the handler for the login stage.
				taskMgr.doMethodLater(0.2, self.response_reader, 'Update Login')
			else:
				# client not connected to login/auth server so display message
				self.updateStatus("Could not connect to the Login server")
				self.showbase.client = False
				self.request_attempt = False
	
	def response_reader(self, task):
		if task.time > 2.5:
			self.loginButton["state"] = DGG.NORMAL
			self.createAccButton["state"] = DGG.NORMAL
			self.updateStatus("Timeout from Login server")
			return task.done
		else:
			temp = self.showbase.client.getData()
			if temp != []:
				for package in temp:
					if len(package) == 2:
						print "Received: " + str(package)
						print "Connected to login server"
						if package[0] == 'login_failed':
							print "Login failed: ", package[1]
							if package[1] == 'username':
								self.updateStatus("Username Doesnt Exist")
								self.passwordBox.set("")
								self.usernameBox.set("")
								self.passwordBox['focus'] = 0
								self.usernameBox['focus'] = 1
							elif package[1] == 'password':
								self.updateStatus("Password Incorrect")
								self.passwordBox.set("")
								self.usernameBox['focus'] = 0
								self.passwordBox['focus'] = 1
							elif package[1] == 'logged':
								self.updateStatus("Username already logged in")
							self.request_attempt = False
							self.loginButton["state"] = DGG.NORMAL
							self.createAccButton["state"] = DGG.NORMAL
							return task.done
						elif package[0] == 'login_valid':
							print "Login valid: ", package[1]
							self.updateStatus(package[1])
							self.update_config()
							self.showbase.start_mainmenu(self)
							return task.done
						elif package[0] == 'create_failed':
							print "Create failed: ", package[1]
							if package[1] == 'exists':
								self.updateStatus("Username Already Exists")
								self.passwordBox.set("")
								self.usernameBox.set("")
								self.passwordBox['focus'] = 0
								self.usernameBox['focus'] = 1
							self.request_attempt = False
							self.loginButton["state"] = DGG.NORMAL
							self.createAccButton["state"] = DGG.NORMAL
							return task.done
						elif package[0] == 'create_success':
							print "Create success", package[1]
							self.updateStatus("Account Created Successfully")
							self.request_attempt = False
							self.attemptLogin()
							return task.done
			return task.cont
		
	def cycleLoginBox(self):
		# function is triggered by the tab key so you can cycle between
		# the two input fields like on most login screens
		if self.passwordBox['focus'] == 1:
			self.passwordBox['focus'] = 0
			self.usernameBox['focus'] = 1
		elif self.usernameBox['focus'] == 1:
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1
		# IMPORTANT: When you change the focus to one of the text boxes,
		# you have to unset the focus on the other textbox.  If you do not
		# do this Panda seems to get confused.
	
	def hide(self):
		self.background.destroy()
		self.usernameText.destroy()
		self.usernameBox.destroy()
		self.usernameStoreBox.destroy()
		self.passwordText.destroy()
		self.passwordBox.destroy()
		self.passwordStoreBox.destroy()
		self.loginButton.destroy()
		self.quitButton.destroy()
		self.createAccButton.destroy()
		self.statusText.destroy()
		
		self.showbase.ignore('tab')
		self.showbase.ignore('shift-tab')
		self.showbase.ignore('enter') 
