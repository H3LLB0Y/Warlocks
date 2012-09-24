from game							import GameData

class User():
	def __init__(self, name, connection = None):
		self.name = name
		self.connection = connection
		self.ready = False
		self.sync = False
		self.gameData = GameData()