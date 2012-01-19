# Spells class idea?

# Also i think we can store it in a db file with sqlite :P
# ill add something like that soon anyway.. 

class Spells:
    def __init__(self, spellLevel):
        # Spell levels? more detail.. dono this is just extra :P.
        self.spellLevel = spellLevel
        
        self.Spells = {}
        # Four elements? for spell types? I guess we can add more :).
        # Fire ofc :D.
        self.Spells['fire'] = {}
        
        # Water. Maybe later we can go into water / ice something.
        self.Spells['water'] = {}
        
        # Earth. splash :P, stun...
        self.Spells['earth'] = {}
        
        # Wind. Can work well with the pushing of players... Wind can be like a basic type.
        self.Spells['wind'] = {}
        
    # Add the spell created to the correct element dict.
    def addFire(self, spellID, makeSpellInstance):
        self.Spells['fire'][spellID] = makeSpellInstance
        print "Fire spell with: %d, Added!. *" % (spellID)
    
    def addWater(self, spellID, makeSpellInstance):
        self.Spells['water'][spellID] = makeSpellInstance
        print "Water spell with: %d, Added!. *" % (spellID)
        
    def addEarth(self, spellID, makeSpellInstance):
        self.Spells['earth'][spellID] = makeSpellInstance
        print "Earth spell with: %d, Added!. *" % (spellID)
        
    def addWind(self, spellID, makeSpellInstance):
        self.Spells['wind'][spellID] = makeSpellInstance
        print "Wind spell with: %d, Added!. *" % (spellID)



# Creating Spells, this part will need most of the data.
# Note this came from my space_project for creating planets.
# So we can change the modelLoad part to something like a particle loader
# or whatever. for the spell it self.
# So mind the extra bits.. :P like spellPath... hehe//
class MakeSpell:
    def __init__(self, spellId, spellName, disc, spellHelpType="Basic"):# spellPath=None, spellNode=None, spellPos=None, spellScale=None):
       
        # We will probly make use of this sometime...
        # ITS AN INT will probly end up going high :P.
        self.spellId = spellId
        
        # Give the spell a name :).
        self.spellName = spellName
        
        # Add some kinda discription to the spell
        # String.
        self.discription = disc
        
        
        ## Well i guess we can add all kinds of things..
        '''
        self.spellDamage = spellDamage
        self.spellManaCost = spellManaCost
        self.spellRate = spellRate
        self.spellElementBonus = spellElementBonus
        self.spellState = spellState
               
        '''
        # Add a model to the planet. or load a particle file or whatever we plan to do :P.
        #self.np = loader.loadModel(modelPath)
        
        # Render it, set it, size it... 
        #self.np.reparentTo(planetNode)
        #self.np.setPos(planetPos)
        #self.np.setScale(planetScale)
        
        # We can give it another type here, unlike the element types, here something like
        # healing, damage, mana, wards... Offensive or Defensive, Support...
        self.spellHelpType = spellHelpType

        # Print out Confirm.
        print "Spell with ID: %d\nDiscription: %s - Created..." % (spellId, disc)


# Make a group maybe? how many levels will we have ? will we have levels :P
spellLevel_1 = Spells("Lvl 1")
spellLevel_2 = Spells("Lvl 2")

# Make a spell :P test...
spell1 = MakeSpell(1, "Fire Ball", "Shoots a fire ball to your target.", "Magic Attack")
spell2 = MakeSpell(2, "Water Spill", "'Drowns the target' leaving him or her Dazed.", "Magic Attack")
spell3 = MakeSpell(3, "Healing Ward", "Places a ward to assist in battle.", "Summoning")
spell4 = MakeSpell(4, "Push", "Basic 'Push' spell.", "Defensive Magic")
spellLevel_1.addFire(1, spell1)
spellLevel_2.addWater(2, spell2)
spellLevel_1.addEarth(3, spell3)
spellLevel_1.addWind(4, spell4)

print "Spells:\nId: %d.		Spell Type: %s" % (spellLevel_1.Spells['fire'][1].spellId, str(spellLevel_1.Spells['earth'][3].spellHelpType))







