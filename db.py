#!/usr/bin/python

# System Imports
import sys, os

# Sql import.
from sqlite3 import dbapi2 as sqlite

# Config (game)
from server_config import *



####>  CODE   <####


# db MainClass.

class DataBase:
	# INIT.
	def __init__(self):
	
		# STATUS is for error msg, or valid msg.
		self.status = ""

		# Check if new_user and pass is valid for creating a new user.
		self.newuser_created = False

		# This keeps the username.. No idea why but i had an reason :P
		self.username_login = ""

		# Check if it was valid.
		self.login_valid = False
		
	# Use the Clients_db function to save and load client account details.
	def Client_acc_add(self, new_user, new_pass):
		# Set the connection to the db.
		self.con = sqlite.connect(SERVER_DB)

		# Set the Cursor for This connection.
		self.cur = self.con.cursor()

		# put user and pass here so we can use it in sql Q.
		self.loginCheck = (new_user, new_pass)

		# Save the userName.
		self.userName = new_user
		self.userPass = new_pass

		# Check if username is available.
		# I'll use caps ok :P
		self.cur.execute("SELECT * FROM accounts ORDER BY acc_name")
		for user in self.cur.fetchall():
			if user[1] == self.userName:
				self.status ="-"+self.userName+"-"+"  "+" already in use!"
				self.cur.close()
				break
			else:
				# Add user if 'name' available.
				self.cur.execute("INSERT INTO accounts(acc_name, acc_pass) VALUES (?, ?)", self.loginCheck)
				self.status = "-"+self.userName+"-"+" "+"Created!"
				self.newuser_created = True
				# Lets save.
				self.con.commit() # ALWAYS!!! other wise it won't save it
				self.cur.close()
		# Close the Cursor and Connection.
		self.cur.close()
		self.con.close()
	###>

	# Used for login checks.
	def Client_getLogin(self, user, passw):

		# Get connection.
		self.con = sqlite.connect(SERVER_DB)

		# Cursor setup.
		self.cur = self.con.cursor()

		self.user = user
		self.passw = passw

		#self.password_valid = False
		# Get the accounts. names/pass
		#self.cur.execute("SELECT acc_name, acc_pass FROM accounts")
		self.cur.execute("select acc_name, acc_pass from accounts where acc_name=:user and acc_pass=:passw",
								{"user": self.user, "passw": self.passw})
		db_data = self.cur.fetchone()
		try:
			if self.passw == db_data[1] and self.user == db_data[0]:
				self.login_valid = True
				print "DB: Login Success" # Console print
				self.status = "Login Success" # To update client.
				self.username_login = db_data[0]
				self.cur.close()
				self.con.close()
				return self.login_valid
		except:
			self.login_valid = False
			self.status = "User & Pass wrong or not found!!"
			print "DB: User & Pass wrong or not found!!"
			self.cur.close()
			self.con.close()
