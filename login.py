from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

import ConfigParser, os

from client							import Client

class Login():
	def __init__(self, showbase, statusText = "Press 'Enter' to login"):
		self.showbase=showbase
		
		self.background = OnscreenImage(
			image  = 'media/gui/login/bg.png',
			parent = render2d
		)
		
		base.setBackgroundColor( 0, 0, 0 )
		# sets the background color to black because the
		# default grey color bugs me for some reason

		self.loginScreen(statusText)
		# draws the login screen

		self.usernameBox['focus'] = 1
		# sets the cursor to the username field by default

		showbase.accept('tab', self.cycleLoginBox)
		# enables the user to cycle through the text fields with the tab key
		# this is a standard feature on most login forms

		showbase.accept('enter', self.attemptLogin)         
		# submits the login form, or you can just click the Login button
		
		# checking variable to stop multiple presses of the button spawn multiple tasks
		self.login_attempt=False
		
		### CONFIG LOADER ###
		config = ConfigParser.RawConfigParser()
		config.read('client.cfg')
		self.LOGIN_IP = config.get('SERVER CONNECTION', 'host_ip')
		self.LOGIN_PORT = config.getint('SERVER CONNECTION', 'host_port')
		### CONFIG END ###
		
		self.showbase.client = Client(self.LOGIN_IP, self.LOGIN_PORT, compress=True)
		if not self.showbase.client.getConnected():
			self.updateStatus("Could not connect to the Login server")
			self.showbase.client=False
		
		self.showbase.username=''
	
	def loginScreen(self,statusText):
		# creates a basic login screen that asks for a username/password
		
		boxloc = Vec3(0.0, 0.0, 0.0)
		# all items in the login form will have a position relative to this
		# this makes it easier to shift the entire form around once we have
		# some graphics to display with it without having to change the
		# positioning of every form element

		# p is the position of the form element relative to the boxloc
		# coordinates set above it is changed for every form element
		p = boxloc + Vec3(-0.22, 0.090, 0.0)                                 
		self.usernameText = OnscreenText(text = "Username:", pos = p, scale = 0.05,bg=(0,0,0,1),fg=(1, 1, 1, 1),align=TextNode.ARight)
		# "Username: " text that appears beside the username box

		p = boxloc + Vec3(-0.2, 0.0, 0.090)
		self.usernameBox = DirectEntry(text = ("") , pos = p, scale=.04, initialText="hunter", numLines = 1) # My testing name :P
		# Username textbox where you type in your username

		p = boxloc + Vec3(-0.22, 0.0, 0.0)       
		self.passwordText = OnscreenText(text = "Password:", pos = p, scale = 0.05,bg=(0,0,0,1),fg=(1, 1, 1, 1),align=TextNode.ARight)
		# "Password: " text that appears beside the password box

		p = boxloc + Vec3(-0.2, 0.0, 0.0)
		self.passwordBox = DirectEntry(text = "" , pos = p, scale=.04, initialText="hunter", numLines = 1, obscured = 1) # Testing password.
		# Password textbox where you type in your password
		# Note - obscured = 1 denotes that all text entered will be replaced
		# with a * like a standard password box
		
		p = boxloc + Vec3( 0, 0, -0.090)
		self.loginButton = DirectButton(text="Login", pos = p,  scale = 0.048, relief=DGG.GROOVE, command=self.attemptLogin)
		# The 'Quit' button that will trigger the Quit function
		# when clicked
		
		p = boxloc + Vec3(0.95, 0, -0.9)
		self.createAccButton = DirectButton(text= "Create Account", scale=0.050, pos = p, relief=DGG.GROOVE, command=self.attemptCreateAccount)
		# Made a quick button for adding accounts. Its fugly

		p = boxloc + Vec3(1.20, 0, -0.9)
		self.quitButton = DirectButton(text="Exit", pos = p,  scale = 0.048, relief=DGG.GROOVE, command=self.showbase.quit)
		# The 'Quit' button that will trigger the Quit function
		# when clicked
		
		p = boxloc + Vec3(0, -0.4, 0)
		self.statusText = OnscreenText(text = statusText, pos = p, scale = 0.043, fg = (1, 0.5, 0, 1), align=TextNode.ACenter)
		# A simple text object that you can display an error/status messages
		# to the user

	def updateStatus(self, statustext):
		self.statusText.setText(statustext)
		# all this does is change the status text.

	def attemptLogin(self):
		# checks to make sure the user inputed a username and password:
		#       if they didn't it will spit out an error message
		#       if they did, it will try to connect to the login server
		#               (under construction)
		self.updateStatus("")
		if(self.usernameBox.get() == ""):
			if(self.passwordBox.get() == ""):
				self.updateStatus("You must enter a username and password before logging in.")
			else:
				self.updateStatus("You must specify a username")
				self.passwordBox['focus'] = 0
				self.usernameBox['focus'] = 1

		elif(self.passwordBox.get() == ""):
			self.updateStatus("You must enter a password")
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1
			
		elif self.usernameBox.get() != "" and self.passwordBox.get() != "":
			self.updateStatus("Attempting to login...")
			# If user and pass is filled in, send it to the login manager.
			return self.attempt_login(self.usernameBox.get(), self.passwordBox.get())
			# why is this returning? does it need to be or does it just need to call the function?
			# because it will return after calling the function anyway
			# was thinking could self.updateStatus() and pass a string back from the attempt_login function to say if couldn't connect or if attempting login
			
	def attemptCreateAccount(self):
		# This checks and creates a new account with the username and password.
		if(self.usernameBox.get() == ""):
			if(self.passwordBox.get() == ""):
				
				self.updateStatus("You must enter a username and password before creating.")
			else:
				self.updateStatus("")
				self.updateStatus("You must specify a username")
				self.passwordBox['focus'] = 0
				self.usernameBox['focus'] = 1

		elif(self.passwordBox.get() == ""):
			self.updateStatus("")
			self.updateStatus("You must enter a password")
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1
		
		elif self.usernameBox.get() != "" and self.passwordBox.get() != "":
			self.updateStatus("")
			# If user and pass is filled in we send the data once again. but this time to createAccount :P
			return self.showbase.create_account(self.usernameBox.get(), self.passwordBox.get())
		
	def cycleLoginBox(self):
		# function is triggered by the tab key so you can cycle between
		# the two input fields like on most login screens

		# IMPORTANT: When you change the focus to one of the text boxes,
		# you have to unset the focus on the other textbox.  If you do not
		# do this Panda seems to get confused.
		if(self.passwordBox['focus'] == 1):
			self.passwordBox['focus'] = 0
			self.usernameBox['focus'] = 1
		elif(self.usernameBox['focus'] == 1):
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1
	
	def attempt_login(self, username, password):
		if not self.login_attempt:
			# attempt to connect again if it failed on startup
			if not self.showbase.client:
				self.showbase.client = Client(self.LOGIN_IP, self.LOGIN_PORT, compress=True)
			if self.showbase.client.getConnected():
				self.login_attempt=True
				self.loginButton["state"]=DGG.DISABLED
				self.showbase.username=username
				# Setup the un/up sendpacket, this will be changed. later :P
				data = {}
				data[0] = 'login_request'
				data[1] = {}
				data[1][0] = username
				data[1][1] = password
				self.showbase.client.sendData(data)
				# Add the handler for the login stage.
				taskMgr.doMethodLater(0.2, self.login_packetReader, 'Update Login')
				return True
			else:
				# client not connected to login/auth server so display message
				self.updateStatus("Could not connect to the Login server")
				self.showbase.client=False
				self.login_attempt=False
	
	def login_packetReader(self, task):
		if task.time>3.0:
			self.loginButton["state"]=DGG.NORMAL
			self.updateStatus("Timeout from Login server")
			return task.done
		else:
			temp=self.showbase.client.getData()
			if temp!=[]:
				for i in range(len(temp)):
					valid_packet=False
					package=temp[i]
					if len(package)==2:
						print "Received: " + str(package)
						print "Connected to login server"
						# updates warlocks in game
						if package[0]=='error':
							print package
							print "User already logged"
							self.updateStatus(package[1])
							self.login_attempt=False
							self.loginButton["state"]=DGG.NORMAL
							return task.done
						if package[0]=='db_reply':
							print "DB: "+str(package[1])
							self.updateStatus(package[1])
							self.login_attempt=False
							self.loginButton["state"]=DGG.NORMAL
							return task.done
						elif package[0]=='login_valid':
							print "Login valid: "+str(package[1])
							self.updateStatus(package[1][0])
							print "success: "+str(package[1][1])
							valid_packet=True
							self.showbase.start_mainmenu()
							return task.done
			return task.cont
	
	def create_account(self, username, password):
		# should be similar to attempt_login() but sends 'create_request' rather than 'login_request'
		# similarly need a create_packetReader() task to check for account_created success packet
		# then automatically call attempt_login with the username and password
		pass
	
	def destroy(self):
		self.background.destroy()
		self.usernameText.destroy()
		self.passwordText.destroy()
		self.usernameBox.destroy()
		self.passwordBox.destroy()
		self.loginButton.destroy()
		self.quitButton.destroy()
		self.createAccButton.destroy()
		self.statusText.destroy()
		
		self.showbase.ignore('tab')
		self.showbase.ignore('enter') 
