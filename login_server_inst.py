from pandac.PandaModules import loadPrcFileData
loadPrcFileData("",
"""
	window-type none
"""
)

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from pandac.PandaModules import *

from login_server_core import LoginServer

class LoginInst(ShowBase):
	def __init__(self):
		ShowBase.__init__(self)
		
		# Start our server up
		print 'STARTING LOGIN SERVER'
		self.LoginServer = LoginServer(9098, compress = True)
		if self.LoginServer.alive:
			taskMgr.doMethodLater(0.5, self.lobby_loop, 'Lobby Loop')
		else:
			print 'Login Server failed to start...'

	# handles new joining clients and updates all clients of chats and readystatus of players
	def lobby_loop(self, task):
		# if in lobby state
		temp = self.LoginServer.getData()
		if temp != []:
			for package in temp:
				# handle client incoming packages here
				if package[0] == 'client':
					# This is where packages will come after clients connect to the server
					# will be things like requesting available servers and chat servers
					if package[1] == 'server_query':
						for server in self.LoginServer.active_servers:
							if server.state == 'lobby':
								self.LoginServer.sendData(
									('server', (server.name, str(server.connection.getAddress()))),
									package[2].connection)
						self.LoginServer.sendData(
							('final', 'No more servers'),
							package[2].connection)
				# handle server incoming packages here
				elif package[0] == 'server':
					# auth
					# game state change
					if len(package[1]) == 2:
						if package[1][0] == 'auth':
							client_auth = False
							print 'Attempting Authentication on: ', package[1][1]
							for client in self.LoginServer.active_clients:
								if client.name == package[1][1]:
									client_auth = True
									break
							if client_auth:
								self.LoginServer.sendData(('auth', client.name), package[2].connection)
							else:
								self.LoginServer.sendData(('fail', package[1][1]), package[2].connection)
						elif package[1][0] == 'state':
							package[2].state = package[1][1]
				# handle chat server incoming packages here
				elif package[0] == 'chat':
					print 'Authorized chat server sent package'
					# handle packages from the chat servers
					# like making public/private
					# authing clients
		return task.again
		
ls = LoginInst()
run()
