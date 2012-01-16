from pandac.PandaModules import CollisionSphere, CollisionNode, Vec3
from math import sin, cos, pi

def move_forwards(rotation, multi):
	# Calculate Change
	x_movement=-sin(rotation*(pi/180))*multi
	y_movement=cos(rotation*(pi/180))*multi
	
	return Vec3(x_movement,y_movement,0)
	
def initCollisionSphere(obj, desc, radiusMultiplier):
		# Get the size of the object for the collision sphere.
		bounds = obj.getChild(0).getBounds()
		center = bounds.getCenter()
		radius = bounds.getRadius() * radiusMultiplier

		# Create a collision sphere and name it something understandable.
		collSphereStr = desc
		cNode = CollisionNode(collSphereStr)
		cNode.addSolid(CollisionSphere(center, radius))

		cNodepath = obj.attachNewNode(cNode)
		#if show:
		#cNodepath.show()

		# Return a tuple with the collision node and its corrsponding string so
		# that the bitmask can be set.
		return (cNodepath, collSphereStr)

# Procedure for setting keys
def set_value(array,key,value):
	# Set key to value
	array[key]=value

def clamp(val, minVal, maxVal): 
	# This function constrains a value such that it is always within or equal to the minimum and maximum bounds. 

	val = min( max(val, minVal), maxVal) 
	# This line first finds the larger of the val or the minVal, and then compares that to the maxVal, taking the smaller. This ensures 
	# that the result you get will be the maxVal if val is higher than it, the minVal if val is lower than it, or the val itself if it's 
	# between the two. 

	return val 
	# returns the clamped value 
