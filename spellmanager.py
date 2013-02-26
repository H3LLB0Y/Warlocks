from spell import Spell
from spellinst import SpellInst
from util import *

class SpellManager:
	def __init__(self):
		# dictionary for holding the current spells
		self.spell_count = 0
		self.spells = {}
		self.active_spells = []
	
	def add_spell(self, spell):
		print self.spell_count, ': adding spell ', spell
		self.spells[self.spell_count] = spell
		self.spell_count += 1
	
	def cast_spell(self, spell_num, caster, pos, rot, worldNP, bullet):
		print "spell: ", spell_num, ": ", caster, " casting spell "
		self.active_spells.append(SpellInst(self.spells[spell_num], caster, pos, rot, worldNP, bullet))
	
	def update(self, dt, usersData, bulletworld):
		for spell in self.active_spells:
			result = spell.update(dt, bulletworld)
			if result == '' or result == 'hit owner':
				pass
			else:
				for user in usersData:
					if result == user.warlock.collNP.getName():
						user.warlock.add_spell_vel(move_forwards(spell.collNP.getH(), spell.spell.target_knockback) * (user.warlock.get_friction() / 1000.0))
						user.warlock.remove_hp(spell.spell.hp)
						user.warlock.add_friction(spell.spell.friction)
						print 'hit warlock ', user.warlock.collNP.getName()
				self.active_spells.remove(spell)
