from pandac.PandaModules import *

# World Class
class World():
	def __init__(self,showbase):
		# Load the environment model (Ground and Surrounding Rocks)
		self.model = showbase.loader.loadModel("media/world/world")
		# Reparent the model to render
		self.model.reparentTo(render)
		# Scale environment
		self.model.setScale(10)

		self.boundaries = {}
		self.addBoundary("boundaryRight", Vec3(1, 0, 0), Point3(-500, 0, 0), (1, 0), (-1, 1))
		self.addBoundary("boundaryLeft", Vec3(-1, 0, 0), Point3(500, 0, 0), (-1, 0), (-1, 1))
		self.addBoundary("boundaryBottom", Vec3(0, -1, 0), Point3(0, 1000, 0), (0, -1), (1, -1))
		self.addBoundary("boundaryTop", Vec3(0, 1, 0), Point3(0, -1000, 0), (0, 1), (1, -1))

	def addBoundary(self, name, orientation, position, posOffset, velMultiplier):
		boundary = CollisionPlane(Plane(orientation, position))
		boundary.setTangible(True)
		self.boundaries[name] = [boundary, posOffset, velMultiplier]
		colNode = self.model.attachNewNode(CollisionNode(name))
		colNode.node().addSolid(boundary)
		colNode.show()

	def collide(self, ball, boundaryName):
		vel = ball.body.getLinearVel()
		pos = ball.body.getPosition()

		b = self.boundaries[boundaryName]
		ball.body.setPosition(pos.getX() + b[1][0], pos.getY() + b[1][1], pos.getZ())
		ball.body.setLinearVel(VBase3(vel[0] * b[2][0], vel[1] * b[2][1], vel[2]))
