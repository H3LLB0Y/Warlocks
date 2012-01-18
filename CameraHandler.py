from direct.showbase import DirectObject 
from pandac.PandaModules import *
import math 
from util import *

# Last modified: 10/2/2009 
# This class takes over control of the camera and sets up a Real Time Strategy game type camera control system. The user can move the camera three 
# ways. If the mouse cursor is moved to the edge of the screen, the camera will pan in that direction. If the right mouse button is held down, the 
# camera will orbit around it's target point in accordance with the mouse movement, maintaining a fixed distance. The mouse wheel will move the 
# camera closer to or further from it's target point. 

# This code was originally developed by Ninth from the Panda3D forums, and has been modified by piratePanda to achieve a few effects. 
# First mod: Comments. I've gone through the code and added comments to explain what is doing what, and the reason for each line of code. 
# Second mod: Name changes. I changed some names of variables and functions to make the code a bit more readable (in my opinion). 
# Third mod: Variable pan rate. I have changed the camera panning when the mouse is moved to the edge of the screen so that the panning 
# rate is dependant on the distance the camera has been zoomed out. This prevents the panning from appearing faster when 
# zoomed in than when zoomed out. I have also added a pan rate variable, which could be modified by an options menu, so it is 
# easier to give the player control over how fast the camera pans. 
# Fourth mod: Variable pan zones. I added a variable to control the size of the zones at the edge of the screen where the camera starts 
# panning. 
# Fifth mod: Orbit limits: I put in a system to limit how far the camera can move along it's Y orbit to prevent it from moving below the ground 
# plane or so high that you get a fast rotation glitch. 
# Sixth mod: Pan limits: I put in variables to use for limiting how far the camera can pan, so the camera can't pan away from the map. These 
# values will need to be customized to the map, so I added a function for setting them. 

class CameraHandler(DirectObject.DirectObject):
	def __init__(self): 
		base.disableMouse() 
		# This disables the default mouse based camera control used by panda. This default control is awkward, and won't be used. 

		base.camera.setPos(0,-35,40) 
		base.camera.lookAt(0,0,0)
		# Gives the camera an initial position and rotation. 

		self.mx,self.my=0,0 
		# Sets up variables for storing the mouse coordinates 

		self.orbiting=False 
		# A boolean variable for specifying whether the camera is in orbiting mode. Orbiting mode refers to when the camera is being moved 
		# because the user is holding down the right mouse button. 

		self.target=Vec3() 
		# sets up a vector variable for the camera's target. The target will be the coordinates that the camera is currently focusing on. 

		self.camDist = 60 
		# A variable that will determine how far the camera is from it's target focus 

		self.panRateDivisor = 10
		# This variable is used as a divisor when calculating how far to move the camera when panning. Higher numbers will yield slower panning 
		# and lower numbers will yield faster panning. This must not be set to 0. 

		self.panZoneSize = .10 
		# This variable controls how close the mouse cursor needs to be to the edge of the screen to start panning the camera. It must be less than 1, 
		# and I recommend keeping it less than .2 

		self.panLimitsX = Vec2(-110, 110) 
		self.panLimitsY = Vec2(-110, 110) 
		# These two vairables will serve as limits for how far the camera can pan, so you don't scroll away from the map.

		self.maxZoomOut = 100
		self.maxZoomIn = 25
		#These two variables set the max distance a person can zoom in or out
		
		self.orbit_rate = 75
		# This is the rate of speed that the camera will rotate when middle mouse is pressed and mouse moved
		# recommended rate 50-100

		self.setTarget(0,0,0) 
		# calls the setTarget function to set the current target position to the origin. 

		self.turnCameraAroundPoint(0,0) 
		# calls the turnCameraAroundPoint function with a turn amount of 0 to set the camera position based on the target and camera distance 

		self.accept("mouse2",self.startOrbit) 
		# sets up the camrea handler to accept a right mouse click and start the "drag" mode. 

		self.accept("mouse2-up",self.stopOrbit) 
		# sets up the camrea handler to understand when the right mouse button has been released, and ends the "drag" mode when 
		# the release is detected.
		
		self.store_x=0
		self.store_y=0
		# for storing of the x and y for the orbit

		# The next pair of lines use lambda, which creates an on-the-spot one-shot function. 

		self.accept("wheel_up",self.zoomIn)
		# sets up the camera handler to detet when the mouse wheel is rolled upwards and uses a lambda function to call the 
		# adjustCamDist function  with the argument 0.9 

		self.accept("wheel_down",self.zoomOut)
		# sets up the camera handler to detet when the mouse wheel is rolled upwards and uses a lambda function to call the 
		# adjustCamDist function  with the argument 1.1 
		
		# Keys array (down if 1, up if 0)
		self.keys={"cam-left":0,"cam-right":0,"cam-up":0,"cam-down":0}
		
		# Using Arrow Keys
		self.accept("arrow_left",set_value,[self.keys,"cam-left",1])
		self.accept("arrow_right",set_value,[self.keys,"cam-right",1])
		self.accept("arrow_up",set_value,[self.keys,"cam-up",1])
		self.accept("arrow_down",set_value,[self.keys,"cam-down",1])
		self.accept("arrow_left-up",set_value,[self.keys,"cam-left",0])
		self.accept("arrow_right-up",set_value,[self.keys,"cam-right",0])
		self.accept("arrow_up-up",set_value,[self.keys,"cam-up",0])
		self.accept("arrow_down-up",set_value,[self.keys,"cam-down",0])
		
		self.key_pan_rate=0.75
		# pan rate for when user presses the arrow keys
		
		# CHESSBOARD STUFF FOR PICKING POINT IN 3D SPACE FROM MOUSE CLICK
		#Since we are using collision detection to do picking, we set it up like
		#any other collision detection system with a traverser and a handler
		self.picker = CollisionTraverser()            #Make a traverser
		self.pq     = CollisionHandlerQueue()         #Make a handler
		#Make a collision node for our picker ray
		self.pickerNode = CollisionNode('mouseRay')
		#Attach that node to the camera since the ray will need to be positioned
		#relative to it
		self.pickerNP = camera.attachNewNode(self.pickerNode)
		#Everything to be picked will use bit 1. This way if we were doing other
		#collision we could seperate it
		self.pickerNode.setFromCollideMask(BitMask32.bit(1))
		self.pickerRay = CollisionRay()               #Make our ray
		self.pickerNode.addSolid(self.pickerRay)      #Add it to the collision node
		#Register the ray as something that can cause collisions
		self.picker.addCollider(self.pickerNP, self.pq)
		#self.picker.showCollisions(render)
		# UNTIL HERE

	def zoomOut(self):
		if(self.camDist <= self.maxZoomOut):
			self.adjustCamDist(1.1)
		return True

	def zoomIn(self):
		if(self.camDist >= self.maxZoomIn):
			self.adjustCamDist(0.9)
		return True

	def turnCameraAroundPoint(self,deltaX,deltaY): 
		# This function performs two important tasks. First, it is used for the camera orbital movement that occurs when the 
		# right mouse button is held down. It is also called with 0s for the rotation inputs to reposition the camera during the 
		# panning and zooming movements. 
		# The delta inputs represent the change in rotation of the camera, which is also used to determine how far the camera 
		# actually moves along the orbit. 

		newCamHpr = Vec3() 
		newCamPos = Vec3() 
		# Creates temporary containers for the new rotation and position values of the camera. 

		camHpr=base.camera.getHpr() 
		# Creates a container for the current HPR of the camera and stores those values. 

		newCamHpr.setX(camHpr.getX()+deltaX) 
		newCamHpr.setY(clamp(camHpr.getY()-deltaY, -85, -10)) 
		newCamHpr.setZ(camHpr.getZ()) 
		# Adjusts the newCamHpr values according to the inputs given to the function. The Y value is clamped to prevent 
		# the camera from orbiting beneath the ground plane and to prevent it from reaching the apex of the orbit, which 
		# can cause a disturbing fast-rotation glitch. 

		base.camera.setHpr(newCamHpr) 
		# Sets the camera's rotation to the new values. 

		angleradiansX = newCamHpr.getX() * (math.pi / 180.0) 
		angleradiansY = newCamHpr.getY() * (math.pi / 180.0) 
		# Generates values to be used in the math that will calculate the new position of the camera. 

		newCamPos.setX(self.camDist*math.sin(angleradiansX)*math.cos(angleradiansY)+self.target.getX())
		newCamPos.setY(-self.camDist*math.cos(angleradiansX)*math.cos(angleradiansY)+self.target.getY()) 
		newCamPos.setZ(-self.camDist*math.sin(angleradiansY)+self.target.getZ()) 
		base.camera.setPos(newCamPos.getX(),newCamPos.getY(),newCamPos.getZ()) 
		# Performs the actual math to calculate the camera's new position and sets the camera to that position. 
		#Unfortunately, this math is over my head, so I can't fully explain it. 

		base.camera.lookAt(self.target.getX(),self.target.getY(),self.target.getZ()) 
		# Points the camera at the target location.
		
	def get_target(self):
		return self.target
		# returns the cur

	def setTarget(self,x,y,z):

		#This function is used to give the camera a new target position. 
		x = clamp(x, self.panLimitsX.getX(), self.panLimitsX.getY()) 
		self.target.setX(x) 
		y = clamp(y, self.panLimitsY.getX(), self.panLimitsY.getY()) 
		self.target.setY(y) 
		self.target.setZ(z) 
		# Stores the new target position values in the target variable. The x and y values are clamped to the pan limits. 

	def setPanLimits(self,xMin, xMax, yMin, yMax): 
		# This function is used to set the limitations of the panning movement. 

		self.panLimitsX = (xMin, xMax) 
		self.panLimitsY = (yMin, yMax) 
		# Sets the inputs into the limit variables. 

	def startOrbit(self): 
		# This function puts the camera into orbiting mode. 

		# Get windows properties
		props = WindowProperties()
		# Set Hide Cursor Property
		#props.setCursorHidden(True)
		# Set properties
		base.win.requestProperties(props)
		# hide cursor

		if base.mouseWatcherNode.hasMouse(): 
			# We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get 
			# a crash error.
			mpos = base.mouseWatcherNode.getMouse()
			self.store_x=mpos.getX()
			self.store_y=mpos.getY()
			# take current cursor values
		
		base.win.movePointer(0,base.win.getXSize()/2,base.win.getYSize()/2)
		# set to center
		self.mx=0
		self.my=0
		
		self.orbiting=True
		# Sets the orbiting variable to true to designate orbiting mode as on. 

	def stopOrbit(self): 
		# This function takes the camera out of orbiting mode. 

		self.orbiting=False 
		# Sets the orbiting variable to false to designate orbiting mode as off. 
		
		base.win.movePointer(0,int((self.store_x+1.0)/2*base.win.getXSize()),int(base.win.getYSize()-((self.store_y+1.0)/2*base.win.getYSize())))
		# set to taken cursor values from startOrbit
		if base.mouseWatcherNode.hasMouse():
			# We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get 
			# a crash error.
			mpos = base.mouseWatcherNode.getMouse()
			self.mx=mpos.getX()
			self.my=mpos.getY()

		# Get windows properties
		props = WindowProperties()
		# Set Hide Cursor Property
		props.setCursorHidden(False)
		# Set properties
		base.win.requestProperties(props)
		# reshow cursor

	def adjustCamDist(self,distFactor): 
		# This function increases or decreases the distance between the camera and the target position to simulate zooming in and out. 
		# The distFactor input controls the amount of camera movement. 
		# For example, inputing 0.9 will set the camera to 90% of it's previous distance. 

		self.camDist=self.camDist*distFactor 
		# Sets the new distance into self.camDist. 

		self.turnCameraAroundPoint(0,0) 
		# Calls turnCameraAroundPoint with 0s for the rotation to reset the camera to the new position.

	def camMoveTask(self,dt):
		# This task is the camera handler's work house. It's set to be called every frame and will control both orbiting and panning the camera. 

		if base.mouseWatcherNode.hasMouse():
			# We're going to use the mouse, so we have to make sure it's in the game window. If it's not and we try to use it, we'll get 
			# a crash error.
			
			mpos = base.mouseWatcherNode.getMouse()
			# Gets the mouse position 

			if self.orbiting: 
				# Checks to see if the camera is in orbiting mode. Orbiting mode overrides panning, because it would be problematic if, while 
				# orbiting the camera the mouse came close to the screen edge and started panning the camera at the same time. 

				self.turnCameraAroundPoint((self.mx-mpos.getX())*self.orbit_rate*dt,(self.my-mpos.getY())*self.orbit_rate*dt)

			else: 
				# If the camera isn't in orbiting mode, we check to see if the mouse is close enough to the edge of the screen to start panning 

				moveY=False 
				moveX=False 
				# these two booleans are used to denote if the camera needs to pan. X and Y refer to the mouse position that causes the 
				# panning. X is the left or right edge of the screen, Y is the top or bottom. 

				if self.my > (1 - self.panZoneSize): 
					angleradiansX1 = base.camera.getH() * (math.pi / 180.0) 
					panRate1 = (1 - self.my - self.panZoneSize) * (self.camDist / self.panRateDivisor)
					moveY = True
				if self.my < (-1 + self.panZoneSize): 
					angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi 
					panRate1 = (1 + self.my - self.panZoneSize)*(self.camDist / self.panRateDivisor) 
					moveY = True
				if self.mx > (1 - self.panZoneSize): 
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5 
					panRate2 = (1 - self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
					moveX = True 
				if self.mx < (-1 + self.panZoneSize): 
					angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5 
					panRate2 = (1 + self.mx - self.panZoneSize) * (self.camDist / self.panRateDivisor) 
					moveX = True 
				# These four blocks check to see if the mouse cursor is close enough to the edge of the screen to start panning and then 
				# perform part of the math necessary to find the new camera position. Once again, the math is a bit above my head, so 
				# I can't properly explain it. These blocks also set the move booleans to true so that the next lines will move the camera. 

				# If up or down keys are pressed
				if (self.keys["cam-up"]^self.keys["cam-down"]):
					moveY = True
					panRate1=self.key_pan_rate
					# Update warlock position on z plane
					if (self.keys["cam-up"]):
						angleradiansX1 = base.camera.getH() * (math.pi / 180.0)+math.pi
					if (self.keys["cam-down"]):
						angleradiansX1 = base.camera.getH() * (math.pi / 180.0)
				
				# If left or right keys are pressed
				if (self.keys["cam-left"]^self.keys["cam-right"]):
					moveX = True 
					panRate2=self.key_pan_rate
					# Update warlock position on x plane
					if (self.keys["cam-left"]):
						angleradiansX2 = base.camera.getH() * (math.pi / 180.0)+math.pi*0.5 
					if (self.keys["cam-right"]):
						angleradiansX2 = base.camera.getH() * (math.pi / 180.0)-math.pi*0.5 
				
				if moveY:
					tempX = self.target.getX()+math.sin(angleradiansX1)*panRate1*dt*50
					tempX = clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY()) 
					self.target.setX(tempX) 
					tempY = self.target.getY()-math.cos(angleradiansX1)*panRate1*dt*50
					tempY = clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY()) 
					self.target.setY(tempY) 
					self.turnCameraAroundPoint(0,0) 
				if moveX:
					tempX = self.target.getX()-math.sin(angleradiansX2)*panRate2*dt*50
					tempX = clamp(tempX, self.panLimitsX.getX(), self.panLimitsX.getY()) 
					self.target.setX(tempX) 
					tempY = self.target.getY()+math.cos(angleradiansX2)*panRate2*dt*50
					tempY = clamp(tempY, self.panLimitsY.getX(), self.panLimitsY.getY()) 
					self.target.setY(tempY) 
					self.turnCameraAroundPoint(0,0) 
				# These two blocks finalize the math necessary to find the new camera position and apply the transformation to the 
				# camera's TARGET. Then turnCameraAroundPoint is called with 0s for rotation, and it resets the camera position based 
				# on the position of the target. The x and y values are clamped to the pan limits before they are applied. 
				#print(self.target)
				self.mx=mpos.getX()
				self.my=mpos.getY()
				# The old mouse positions are updated to the current mouse position as the final step. 
	
	def get_mouse_3d(self):
		#Set the position of the ray based on the mouse position
		if base.mouseWatcherNode.hasMouse():
			mpos = base.mouseWatcherNode.getMouse()
			self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
			
			nearPoint = render.getRelativePoint(camera, self.pickerRay.getOrigin())
			#Same thing with the direction of the ray
			nearVec = render.getRelativeVector(camera, self.pickerRay.getDirection())
			destination=PointAtZ(0, nearPoint, nearVec)
			return destination
		return Vec3(-1,-1,-1)

#This function, given a line (vector plus origin point) and a desired z value,
#will give us the point on the line where the desired z value is what we want.
#This is how we know where to position an object in 3D space based on a 2D mouse
#position. It also assumes that we are dragging in the XY plane.
#
#This is derived from the mathmatical of a plane, solved for a given point
def PointAtZ(z, point, vec):
  return point + vec * ((z-point.getZ()) / vec.getZ())
# STOLEN FROM CHESSBOARD EXAMPLE
