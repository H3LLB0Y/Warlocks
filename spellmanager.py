from spell import Spell
from spellinst import SpellInst
from util import *

class SpellManager:
	def __init__(self,num_warlocks):
		# dictionary for holding the current spells
		self.spell_count=0
		self.spells={}
		self.active_spells=[]
		self.num_warlocks=num_warlocks
	
	def add_spell(self,spell):
		print str(self.spell_count)+': adding spell '+str(spell)
		self.spells[self.spell_count]=spell
		self.spell_count+=1
	
	def cast_spell(self,spell_num,caster,pos,rot,worldNP,bullet):
		print "spell: "+str(spell_num)+": "+str(caster)+" casting spell "
		self.active_spells.append(SpellInst(self.spells[spell_num],caster,pos,rot,worldNP,bullet))
	
	def update(self,dt,warlocks,bulletworld):
		for x in self.active_spells:
			result=x.update(dt,bulletworld)
			if result=='' or result=='hit owner':
				pass
			else:
				for i in range(self.num_warlocks):
					if result==warlocks[i][0]:
						warlocks[i][1].add_spell_vel(move_forwards(x.collNP.getH(),x.spell.target_knockback))
						warlocks[i][1].add_damage(x.spell.damage)
						print 'hit warlock '+warlocks[i][0]
				x.remove_me=True
		for x in self.active_spells:
			if x.remove_me:
				self.active_spells.remove(x)
