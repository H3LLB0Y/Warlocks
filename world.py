from pandac.PandaModules import *
from util import *

# World Class
class World():
	def __init__(self,showbase,num_warlocks):
		# Load the environment model (Ground and Lava Rocks)
		#self.model = showbase.loader.loadModel("media/world/arena")
		# Reparent the model to render
		#self.model.reparentTo(render)
		model = showbase.loader.loadModel("media/world/world")
		# extract the ground from the model
		#self.world=model.find("**/Ground")
		#self.world.reparentTo(render)
		
		# generate n gon for platform
		world_col={}
		n_gon=self.create_world(num_warlocks,world_col)
		self.world=render.attachNewNode(n_gon)
		self.n_col=self.world.attachNewNode(CollisionNode('world_col'))
		for i in range(num_warlocks):
			self.n_col.node().addSolid(world_col[i])
			self.n_col.show()
		
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
	
	def create_world(self,n,world_col):
		# make it at least a square
		if n<4:
			n=4
		
		points={}
		
		# rotation between each warlock for even spacing
		rotation=360.0/n
		
		for i in range(n):
			# adjust rotation for this warlock
			rot=rotation*(i+1)
			
			# set its position 10*n+15 units from center
			points[i]=move_forwards(rot,-10.0*n-25.0)
			
		nnode=GeomNode('n_gon')
		for i in range(n):
			nnode.addGeom(self.create_triangle(points[i],points[(i+1)%n]))
			world_col[i]=CollisionPolygon(points[i],points[(i+1)%n],Point3(0,0,0.1))
			
		return nnode
		
	def create_triangle(self,point1,point2):
		format=GeomVertexFormat.getV3n3cpt2()
		vdata=GeomVertexData('triangle', format, Geom.UHStatic)

		vertex=GeomVertexWriter(vdata, 'vertex')
		normal=GeomVertexWriter(vdata, 'normal')
		color=GeomVertexWriter(vdata, 'color')
		texcoord=GeomVertexWriter(vdata, 'texcoord')
		
		# first point
		vertex.addData3f(point1.getX(), point1.getY(), 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(1, 0)

		# second point
		vertex.addData3f(point2.getX(), point2.getY(), 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(1, 1)

		# center point (0,0,0)
		vertex.addData3f(0, 0, 0.1)
		normal.addData3f(0, 0, 1)
		color.addData4f(1, 1, 1, 1)
		texcoord.addData2f(0, 1)
		
		tri1=GeomTriangles(Geom.UHStatic)

		tri1.addVertex(0)
		tri1.addVertex(1)
		tri1.addVertex(2)
		
		tri1.closePrimitive()
		
		triangle=Geom(vdata)
		triangle.addPrimitive(tri1)
		
		return triangle
