from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *


class Login():
	def __init__(self, game, statusText = "Press 'Enter' to login"):
		self.game=game
		
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

		game.accept('tab', self.cycleLoginBox)
		# enables the user to cycle through the text fields with the tab key
		# this is a standard feature on most login forms

		game.accept('enter', self.attemptLogin)         
		# submits the login form, or you can just click the Login button
	
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
		self.quitButton = DirectButton(text="Exit", pos = p,  scale = 0.048, relief=DGG.GROOVE, command=self.game.quit)
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
			return self.game.attempt_login(self.usernameBox.get(), self.passwordBox.get())
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
			return self.game.create_account(self.usernameBox.get(), self.passwordBox.get())
		
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
		
		self.game.ignore('tab')
		self.game.ignore('enter') 
