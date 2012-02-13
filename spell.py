class Spell:
	MODELS={0:'media/spells/blockyball',1:'media/spells/pointyball'}
	def __init__(self):
		self.damage=0
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
		array[0]=self.damage
		array[1]=self.target_knockback
		array[2]=self.self_knockback
		array[3]=self.range
		array[4]=self.speed
		array[5]=self.aoe
		array[6]=self.aoe_range
		array[7]=self.targeting
		array[8]=self.casting_time
		array[9]=self.interruptable
		array[10]=self.model
		return array
	
	def receive(self,array):
		self.damage=array[0]
		self.target_knockback=array[1]
		self.self_knockback=array[2]
		self.range=array[3]
		self.speed=array[4]
		self.aoe=array[5]
		self.aoe_range=array[6]
		self.targeting=array[7]
		self.casting_time=array[8]
		self.interruptable=array[9]
		self.model=array[10]
