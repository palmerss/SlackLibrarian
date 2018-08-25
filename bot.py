import time
import event
import sqlite3
from slackclient import SlackClient
from pathlib import Path

class Bot(object):
	def __init__(self):
		#initializes a new Library SQLLite File
		my_file = Path("library")
		if (not my_file.is_file()):
			self.libraryINIT()

		#initialize the bots log
		my_file = Path("LibraryLog.log")
		if (not my_file.is_file()):
			print ("No log detected, creating new one")
			LibraryLog = open("LibraryLog.log", "w")
			LibraryLog.writelines("LOG INITIALIZED \n")
			LibraryLog.close()

		self.slack_client = SlackClient("xoxb-403303008263-402160290483-prTeUIWAM3hziOyE1rgIOs0N")
		self.bot_name = "librarian"
		self.bot_id = self.get_bot_id()
		
		if self.bot_id is None:
			print('Could not find librarian')
			exit("Error, could not find " + self.bot_name)
	
		self.event = event.Event(self)
		self.listen()
	
	def get_bot_id(self):
		api_call = self.slack_client.api_call("users.list")
		if api_call.get('ok'):
			# retrieve all users so we can find our bot
			users = api_call.get('members')
			for user in users:
				if 'name' in user and user.get('name') == self.bot_name:
					return "<@" + user.get('id') + ">"
			return None
			
	def listen(self):
		if self.slack_client.rtm_connect(with_team_state=False):
			print("Successfully connected, listening for commands")
			while True:
				self.event.wait_for_event()
				time.sleep(1)
		else:
			print("connection failed")
			exit("Error, Connection Failed")

	def libraryINIT(self):
		library = sqlite3.connect('library')
		curser = library.cursor()
		curser.execute(''' CREATE TABLE books(title PRIMARY KEY,
	     author TEXT,
	     owner TEXT,
	     checkedOutBy TEXT,
	     checkoutDate TEXT) ''')
		library.commit()
		print ("No library detected, created new one")