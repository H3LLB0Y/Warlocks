from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *

class PreLobby():
	def __init__(self, game, statusText = ""):
		self.game=game
		
		self.background = OnscreenImage(
			image  = 'media/gui/bg.jpg',
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


		# Adding a frame for looks.
		p = boxloc + Vec3(-0.15, 0.0, 0.0)
		self.loginFrame = DirectFrame (image = ('media/gui/frame.png'), image_scale = (0.4, 0.4, 0.35))
		
		# p is the position of the form element relative to the boxloc
		# coordinates set above it is changed for every form element
		#p = boxloc + Vec3(-0.5, 0, 0.0)                                 
		#self.usernameText = OnscreenText(text = "Username:", pos = p, scale = 0.07,bg=(0,0,0,1),fg=(1, 1, 1, 1),align=TextNode.ALeft)
		# "Username: " text that appears beside the username box

		p = boxloc + Vec3(-0.3, 0, 0.048)
		self.usernameBox = DirectEntry(text = "" , pos = p, scale=.04, initialText="", numLines = 1)
		# Username textbox where you type in your username

		#p = boxloc + Vec3(-0.5, -0.1, 0.0)       
		#self.passwordText = OnscreenText(text = "Password:", pos = p, scale = 0.07,bg=(0,0,0,1),fg=(1, 1, 1, 1),align=TextNode.ALeft)
		# "Password: " text that appears beside the password box

		p = boxloc + Vec3(-0.3, 0, -0.096)
		self.passwordBox = DirectEntry(text = "" , pos = p, scale=.04, initialText="", numLines = 1, obscured = 1)
		# Password textbox where you type in your password
		# Note - obscured = 1 denotes that all text entered will be replaced
		# with a * like a standard password box

		p = boxloc + Vec3(0, 0, -0.23)
		self.loginButton = DirectButton(image = ('media/gui/login_bt.png'), pos = p,  scale = 0.14, image_scale = (0.48, 0.48, 0.34), command=self.attemptLogin)
		# The 'Login' button that will trigger the attemptLogin function
		# when clicked
		
		p = boxloc + Vec3(0.2, 0, -0.23)
		self.quitButton = DirectButton(image = ('media/gui/exit_bt.png'), pos = p, scale = 0.14, image_scale = (0.48, 0.48, 0.34),  command=self.game.quit)
		# The 'Quit' button that will trigger the Quit function
		# when clicked

		p = boxloc + Vec3(0, -0.4, 0)
		self.statusText = OnscreenText(text = statusText, pos = p, scale = 0.05, fg = (1, 0, 0, 1), align=TextNode.ACenter)
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

		if(self.usernameBox.get() == ""):
			if(self.passwordBox.get() == ""):
				self.updateStatus("NOTE: You must enter a username and password before logging in.")
			else:
				self.updateStatus("ERROR: You must specify a username")
				self.passwordBox['focus'] = 0
				self.usernameBox['focus'] = 1

		elif(self.passwordBox.get() == ""):
			self.updateStatus("ERROR: You must enter a password")
			self.usernameBox['focus'] = 0
			self.passwordBox['focus'] = 1

		else:
			self.updateStatus("")
			# this is where the networking code will get put in
			self.game.login(self.usernameBox.get(),self.passwordBox.get())

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
		#self.title.destroy()
		self.loginFrame.destroy()
		#self.usernameText.destroy()
		#self.passwordText.destroy()
		self.usernameBox.destroy()
		self.passwordBox.destroy()
		self.loginButton.destroy()
		self.quitButton.destroy()
		self.statusText.destroy()
		
		self.game.ignore('tab')
		self.game.ignore('enter') 
