class Spell:
	MODELS={0:'media/spells/blockyball',1:'media/spells/pointyball'}
	def __init__(self):
		self.hp=0
		self.friction=0
		self.target_knockback=0
		self.self_knockback=0
		self.range=0
		self.speed=0
		self.aoe=False
		self.aoe_range=0
		self.targeting=False
		self.casting_time=0
		self.interruptable=False
		self.model=0
	
	def send(self):
		array={}
		array[0]=self.hp
		array[1]=self.friction
		array[2]=self.target_knockback
		array[3]=self.self_knockback
		array[4]=self.range
		array[5]=self.speed
		array[6]=self.aoe
		array[7]=self.aoe_range
		array[8]=self.targeting
		array[9]=self.casting_time
		array[10]=self.interruptable
		array[11]=self.model
		return array
	
	def receive(self,array):
		self.hp=array[0]
		self.friction=array[1]
		self.target_knockback=array[2]
		self.self_knockback=array[3]
		self.range=array[4]
		self.speed=array[5]
		self.aoe=array[6]
		self.aoe_range=array[7]
		self.targeting=array[8]
		self.casting_time=array[9]
		self.interruptable=array[10]
		self.model=array[11]
