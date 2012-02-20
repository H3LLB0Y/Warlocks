from direct.gui.DirectGui     import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText  import OnscreenText
from pandac.PandaModules      import *
from panda3d.rocket				import *

from spell							import Spell
from spellmanager					import SpellManager

class MessageDataSource(DataSource):
	def __init__(self,name):
		self.messages = []
		DataSource.__init__(self,name)
		
	def add_new_message(self,name,message):
		self.messages.append({'name':name,'message':message})
	
	def GetRow(self, table_name, index, columns):
		row = list()
		try:
			if index > len(self.messages)-1:
				return row
			if table_name == 'messages':
				for col in columns:
					if col not in self.messages[index]:
						continue
					if col == 'name':
						row.append(self.messages[index][col])
					elif col == 'message':
						row.append(self.messages[index][col])
		except:
			traceback.print_exc()
		return row 

	def GetNumRows(self, table_name):
		if table_name=='messages':
			return len(self.messages)
		return 0
		
class PlayersDataSource(DataSource):
	def __init__(self,name):
		self.players = []
		DataSource.__init__(self,name)
		
	def update_players(self,name,ready):
		player_found=False
		for p in self.players:
			if p['name']==name:
				p['ready']=ready
				player_found=True
				break
		if not player_found:
			self.players.append({'name':name,'ready':ready})
	
	def GetRow(self, table_name, index, columns):
		row = list()
		try:
			if index > len(self.players)-1:
				return row
			if table_name == 'players':
				for col in columns:
					if col not in self.players[index]:
						continue
					if col == 'name':
						row.append(self.players[index][col])
					elif col == 'ready':
						row.append(self.players[index][col])
		except:
			traceback.print_exc()
		return row 

	def GetNumRows(self, table_name):
		if table_name=='players':
			return len(self.players)
		return 0
		
class SpellsDataSource(DataSource):
	def __init__(self,name):
		self.spells = []
		DataSource.__init__(self,name)
		
	def add_spell(self,spell):
		pass
	
	def GetRow(self, table_name, index, columns):
		row = list()
		try:
			if table_name == 'spells':
				if index > len(self.spells)-1:
					return row 
				for col in columns:
					if col not in self.spells[index]:
						continue
					if col == 'name':
						row.append(self.spells[index][col])
					elif col == 'ready':
						row.append(self.spells[index][col])
		except:
			traceback.print_exc()
		return row 

	def GetNumRows(self, table_name):
		if table_name=='spells':
			return len(self.spells)
		return 0

class Pregame():
	def __init__(self, showbase):
		self.showbase=showbase
		
		self.ready=False
		
		LoadFontFace("gui/Delicious-Bold.otf")

		self.messagesdatasource = MessageDataSource('messages')
		self.playersdatasource = PlayersDataSource('players')
		
		self.rocket=RocketRegion.make('warlocksRocket',base.win)
		self.rocket.setActive(1)
		self.context=self.rocket.getContext()
		
		self.bg = self.context.LoadDocument('gui/pregame-bg.rml')
		self.bg.Show()
		
		self.doc = self.context.LoadDocument('gui/pregame-layout.rml')
		self.doc.Show()

		ih = RocketInputHandler()
		base.mouseWatcher.attachNewNode(ih)
		self.rocket.setInputHandler(ih)
		
		self.send_button = self.doc.GetElementById('send_button')
		self.send_button.AddEventListener('click',self.send_message,True)
		
		self.message = self.doc.GetElementById('message_box')
		self.showbase.accept("enter",self.send_message)
		self.messages=self.doc.GetElementById('messages')
		
		self.players=self.doc.GetElementById('players')
		
		self.ready_button = self.doc.GetElementById('ready_button')
		self.ready_button.AddEventListener('click',self.toggle_ready,True)
		
		# disconnect button (should return back to the lobby, atmo just exiting)
		self.disconnect_button = self.doc.GetElementById('disconnect_button')
		self.disconnect_button.AddEventListener('click',self.disconnect,True)

		# Add the game loop procedure to the task manager.
		taskMgr.doMethodLater(1.0, self.update_lobby, 'Update Lobby')
	
	def update_lobby(self, task):
		temp=self.showbase.client.getData()
		if temp!=[]:
			for i in range(len(temp)):
				valid_packet=False
				package=temp[i]
				if len(package)==2:
					print "Received: " + str(package)
					if package[0]=='auth':
						# if authenticated then receive all the spells and warlocks
						print 'Authenticated YEAH!!!'
					# if username is sent, assign to client
					elif package[0]=='chat':
						print "Chat: "+self.showbase.clients[package[1][0]]+' said: '+package[1][1]
						self.messagesdatasource.add_new_message(self.showbase.clients[package[1][0]],package[1][1])
						self.messages.SetDataSource('messages.messages')
					elif package[0]=='spell':
						spell=Spell()
						spell.receive(package[1])
						self.showbase.spells.append(spell)
					elif package[0]=='client':
						self.showbase.clients[package[1][0]]=package[1][1]
						self.showbase.num_warlocks+=1
						self.playersdatasource.update_players(package[1][1],'Unready')
						self.players.SetDataSource('players.players')
						print 'client '+str(package[1][0])+' '+str(package[1][1])
					elif package[0]=='ready':
						self.playersdatasource.update_players(package[1][0],package[1][1])
						self.players.SetDataSource('players.players')
						print 'ready '+str(package[1][0])+' '+str(package[1][1])
					elif package[0]=='which':
						self.showbase.which=package[1]
						print "i am warlock: "+str(package[1])
					# changes to game state (i guess this could be done the same as the gamestate ones, all but this change state packet, which will be same
					elif package[0]=='state':
						print "state: "+package[1]
						if package[1]=='preround':
							self.showbase.start_preround()
							return task.done
				else:
					print "Packet wrong size"
			
		return task.again
	
	def toggle_ready(self):
		if self.ready:
			self.ready=False
			data = {}
			data[0] = "unready"
			data[1] = "unready"
			self.showbase.client.sendData(data)
		else:
			self.ready=True
			data = {}
			data[0] = "ready"
			data[1] = "ready"
			self.showbase.client.sendData(data)
		
	def disconnect(self):
		data = {}
		data[0] = "disconnect"
		data[1] = "disconnect"
		self.showbase.client.sendData(data)
		self.showbase.quit()
	
	def send_message(self):
		if self.message.GetAttribute('value')!='':
			data = {}
			data[0] = "chat"
			data[1] = self.message.GetAttribute('value')
			self.message.SetAttribute('value','')
			self.showbase.client.sendData(data)

	def hide(self):
		self.bg.Hide()
		self.doc.Hide()
