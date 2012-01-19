class Skybox():
	def __init__(self,game):
		# Skybox Setup
		skyBox=loader.loadModel("media/skybox/Skybox.egg")
		skyBox.setBin("background",1)
		skyBox.setScale(1,1,1)
		skyBox.setDepthTest(False)
		skyBox.setZ(render,0)
		skyBox.setShaderOff()
		skyBox.setLightOff()
		skyBox.setCompass()
		skyBox.reparentTo(game.camera)
		# End Skybox Setup
