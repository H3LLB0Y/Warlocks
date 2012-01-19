from pandac.PandaModules import *

# World Class
class World():
	def __init__(self,showbase):
		# Load the environment model (Ground and Lava Rocks)
		#self.model = showbase.loader.loadModel("media/world/arena")
		# Reparent the model to render
		#self.model.reparentTo(render)
		model = showbase.loader.loadModel("media/world/world")
		# extract the ground from the model
		self.world=model.find("**/Ground")
		self.world.reparentTo(render)
		# extract lava from the model
		self.lava=model.find("**/Lava")
		self.lava.reparentTo(render)
		
		"""# Add a light to the scene.
		self.lightpivot = render.attachNewNode("lightpivot")
		self.lightpivot.setPos(0,0,25)
		self.lightpivot.hprInterval(10,Point3(360,0,0)).loop()
		plight = PointLight('plight')
		plight.setColor(Vec4(1, 1, 1, 1))
		plight.setAttenuation(Vec3(0.7,0.05,0))
		plnp = self.lightpivot.attachNewNode(plight)
		plnp.setPos(45, 0, 0)
		self.world.setLight(plnp)
		self.world.setShaderInput("light", plnp)
		
		# Add an ambient light
		alight = AmbientLight('alight')
		alight.setColor(Vec4(0.2, 0.2, 0.2, 1))
		alnp = render.attachNewNode(alight)
		self.world.setLight(alnp)
		
		self.world.setShaderAuto()"""
		
		self.proj = render.attachNewNode(LensNode('proj'))
		self.lens = OrthographicLens()
		self.lens.setFilmSize(250)
		self.proj.node().setLens(self.lens)
		self.proj.reparentTo(render)
		self.proj.setPos(0,0,1)
		self.proj.lookAt(0,0,0)

		self.tex = loader.loadTexture('media/world/textures/Mapzone Editz/fieldstone-c.jpg')
		#self.norm = loader.loadTexture('media/world/textures/Mapzone Editz/fieldstone-n.jpg')
		self.ts = TextureStage('ts')
		
		"""self.boundaries = {}
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
		ball.body.setLinearVel(VBase3(vel[0] * b[2][0], vel[1] * b[2][1], vel[2]))"""
	
	def raise_lava(self):
		self.world.setScale(self.world,0.9999)
		self.world.clearTexture()
		#self.ts.setMode(TextureStage.MReplace)
		self.world.projectTexture(self.ts, self.tex, self.proj)
		#self.ts.setMode(TextureStage.MNormal)
		#self.world.projectTexture(self.ts, self.norm, self.proj)
		

		
