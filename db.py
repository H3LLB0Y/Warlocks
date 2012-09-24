from sqlite3 import dbapi2 as sqlite

class ClientDataBase:
	def __init__(self):
		self.connection = sqlite.connect('databases/client_db')
		if self.connection:
			self.connected = True
		else:
			self.connected = False

	def __del__(self):
		if self.connection:
			self.connection.close()
				
	# Use the Clients_db function to save and load client account details.
	def add_client(self, username, password):
		# Set the Cursor for This connection.
		cur = self.connection.cursor()

		# Check if username is available.
		cur.execute("SELECT * FROM accounts ORDER BY acc_name")
		user_found = False
		for user in cur.fetchall():
			if user[1] == username:
				print username, " already in use!"
				user_found = True
				returns = False, 'exists'
				break
		if not user_found:
			# Add user if 'name' available.
			cur.execute("INSERT INTO accounts(acc_name, acc_pass) VALUES (:username, :password)",
								{ "username": username, "password": password })
			print username, " Created!"
			returns = True, 'success'
			connection.commit()
		# Close the Cursor and Connection.
		cur.close()

		return returns

	# Used for login checks.
	def validate_client(self, username, password):
		# Cursor setup.
		cur = self.connection.cursor()

		# Get the accounts. names/pass
		cur.execute("select acc_name, acc_pass from accounts where acc_name=:username",
								{"username": username})
		db_data = cur.fetchone()
		if db_data == None:
			returns =  False, 'username'
		elif password == db_data[1]:
			returns = True, 'success'
		else:
			returns = False, 'password'
		cur.close()

		return returns
