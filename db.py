#!/usr/bin/python

# System Imports
import sys, os

# Sql import.
from sqlite3 import dbapi2 as sqlite

# Config (game)
from server_config import *

# Panda Imports


####>  CODE   <####

# db MainClass.

class DataBase:
    
    
    # INIT.
    def __init__(self):
        pass 
    
    # Use the Clients_db function to save and load client account details.
    def Clients_db(self, new_user):
        
        # Set the connection to the db.
        self.conn = sqlite.connect(SERVER_DB)
         
        # Set the Cursor for This connection.
        self.cur = self.conn.cursor()
        
        self.new_user = []
        self.new_user.append(new_user)

        self.cur.execute("insert into accounts(acc_name) values (?)", self.new_user)
        
        # Lets save.
        self.conn.commit()
         
        # Close the Cursor and Connection.
        self.cur.close()
        self.conn.close()
         
    ###>
    
   
db = DataBase()

db.Clients_db("Test User")




















