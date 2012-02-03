#!/usr/bin/env python
#

# Spell Manager server side.

class SpellsMgr:
    
    def doMove(self, net_users, net_package=0):
        
        package = net_package
        users = net_users
        
        for u in range(len(self.users)):
            if self.users[u]['new_dest']:
                data = {}
                data[0]='update'
                data[1]=u
                data[2]={}
                data[2][0]=self.users[u]['warlock'].destination.getX()
                data[2][1]=self.users[u]['warlock'].destination.getY()
                self.users[u]['new_dest']=False
                self.server.broadcastData(data)





'''
## This is for the spells idea.

client has [code] and [script]

server has [code+check] and [script]



under Client:
	# When client request the use of a spell. Lets say SPELL_x1 = fire
	if playerUse['q']: # Check the button press / Use
		client.sendData(playerdata, targetData, 'SPELL_x1') # Send the packet regarding the data for the Source, Target, and whatever
	
	if packetfromServer say ['DO_CAST']	
		runSpell['q'] # Run the script/math on the client



server :
	getData() from clients # Get packets from clients/data
	read packets # Read and sort to functions.
	if spellID == ('SPELL_x1'): # Check for the spells
		runSpeLL script(sendparams(source, target)
		sendData to source(source, target'DO_CAST')
		sendData to target('DO_SPELL_SCRIPT')
		tick()

spell script(source, target):
	caster = source 
	enemy = target
	
	
'''	
	
	
	
	
