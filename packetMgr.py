# I will atempt t write a packet handler/manager for the sending and recieving of packets.
# For now this is useless... I guess because we will have like 3 to for if anyway... we can probly use or between the spells.. 

# PacketHandler.
'''
class PacketMgr:
	
	def __init__(self):
		pass 
		
	
	# The Do section. 
	# This will be for sending 'update' packets to clients.
	def doMove(self, users, ):
		print "DOING MOVE"
		
	def doCast(self):
		pass
		
	def doChat(self):
		pass

'''
# Other random idea code..

'''
Make a system/function for In lobby hosted games discovery and selection.

maak n system wat die hosted games laat oppop langs die kant.  soos a desktop.
- dan kan clients kies wat ever hulle wil wanner hulle wil, kry dit 
- laat mens die group/setup deel skip en dit alles op een slag doen in lobby.
- so dit pop dan op sodra die creator sy shit gekies het.. dan float dit half aan die kant of wherever.

'''

# Class to handle the lobby and gameHosts at same time...
# mini popup in game list, user click join and client connects to that game via ip, hostName.
# Instance to make that will fit self.hostList = LiceGames(self)
class LiveGames:
    
        def __init__(self, state):
                self.state = state
                self.hosted = {}
                self.hosted[0] = {}
    
    
    
        def addHostToList(self, hostIp, hostGame):
                self.hosted[hostIp] = hostGame # Use ip in data. So later we use livegames.connect[hostIp].
                # Name to show in lobby.
                # This is for available slots.
                # Maybe later add something like a ping/lag status. '200ms'
                # Host location. 'EU, US, NZ, ZA, NL'
    
    

hostList = LiveGames('lobby game list')




    
class CreateGame:
    
        def __init__(self, gameName, hostIp, gameMap, gameSlots):
            
                self.game_name = gameName
                self.host_ip = hostIp
                self.game_map = gameMap
                self.game_slots = gameSlots
                # 

game1 = CreateGame('My Game', '127.0.0.1', 'Arena', 8)

hostList.addHostToList(game1.host_ip, game1)

print hostList.hosted['127.0.0.1'].game_name # Run a loop to check for hosted games.
    
    
    
    
    
    
    
    
