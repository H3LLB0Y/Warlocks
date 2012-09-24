from spell import Spell
from spellinst import SpellInst
from util import *

class SpellManager:
	def __init__(self, warlocks):
		# dictionary for holding the current spells
		self.spell_count = 0
		self.spells = {}
		self.active_spells = []
	
	def add_spell(self, spell):
		print self.spell_count, ': adding spell '+str(spell)
		self.spells[self.spell_count]=spell
		self.spell_count+=1
	
	def cast_spell(self, spell_num, caster, pos, rot, worldNP, bullet):
		print "spell: ", spell_num, ": ", caster, " casting spell "
		self.active_spells.append(SpellInst(self.spells[spell_num], caster, pos, rot, worldNP, bullet))
	
	def update(self, dt, warlocks, bulletworld):
		for x in self.active_spells:
			result = x.update(dt, bulletworld)
			if result == '' or result == 'hit owner':
				pass
			else:
				for warlock in warlocks:
					if result == warlock.warlock.collNP.getName():
						warlock.warlock.add_spell_vel(move_forwards(x.collNP.getH(),x.spell.target_knockback)*(warlock.warlock.get_friction()/1000.0))
						warlock.warlock.remove_hp(x.spell.hp)
						warlock.warlock.add_friction(x.spell.friction)
						print 'hit warlock ', warlock.warlock.collNP.getName()
				x.remove_me = True
		for x in self.active_spells:
			if x.remove_me:
				self.active_spells.remove(x)
