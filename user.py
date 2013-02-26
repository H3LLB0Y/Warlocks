class UserData():
	def __init__(self):
		self.new_dest = False
		self.new_spell = False
		self.warlock = None
		self.thisPlayer = False

	def makeUpdatePackets(self):
		packets = []
		# new destination
		if self.new_dest:
			packets.append(('update_dest', self.warlock.get_destination_update()))
			self.new_dest = False
		# new spell
		if self.new_spell:
			packets.append(('update_spell', self.warlock.get_spell_update()))
			self.new_spell = False
		return packets

	def processUpdatePacket(self, packet):
		if len(packet) == 2:
			if packet[0] == 'update_dest':
				self.warlock.set_destination(packet[1])
				self.new_dest = True
			elif packet[0] == 'update_spell':
				self.warlock.set_spell(packet[1])
				self.new_spell = True

class User():
	def __init__(self, name, connection = None):
		self.name = name
		self.connection = connection
		self.ready = False
		self.sync = False
		self.gameData = UserData()