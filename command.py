import re
import sqlite3
import datetime

class Command(object):
	def __init__(self):
		self.commandREGEX = re.compile('^.*?(?=\s)')
		self.parameterREGEX = re.compile('(?=^.*?\s(.*))')
		self.commands = { 
			"addbook"     : self.addBook,
			"showlibrary" : self.showLibrary,
			"editbook"    : self.editBook,
			"checkout"    : self.checkoutBook,
			"return"      : self.returnBook,
			"removebook"      : self.removeBook,
			"help"        : self.help
		}

	def handle_command(self, user, input, slackClient):
		response = "<@" + user + ">: \n"
		command = ""
		parameters = ""
		self.slackCLient = slackClient
		self.user = "<@" + user + "> "

		#Collect command
		if(self.commandREGEX.search(input)):
			command = self.commandREGEX.match(input).group()

		#Collect parameters
		if(self.parameterREGEX.search(input)):
			parameters = self.parameterREGEX.match(input).group(1)

		#this condition is helpful for commands that don't have parameters.
		if(command == ""):
			command=input;

		#COMMAND NOT IN COMMAND LIST
		if command in self.commands:
			response += self.commands[command](parameters)
		else:
			response += "Sorry I don't understand the command: " + command + ". " + self.help("")

		#RESET USER
		self.user=""
		return response
		
	def addBook(self, parameters):
		title = parameters
		author = "N/A"
		owner = "N/A"
		result = "BOOK ADDED"

		#SQLLITE CONNECTION
		library = sqlite3.connect('library')

		#PARAMETER PARSING
		title = title.replace("\"", "")

		#SQL MAGIC
		try:
			library.execute('''INSERT INTO books(title, author, owner, checkedOutBy, checkoutDate)
		    		 VALUES(?,?,?,?,?)''', (title, author, owner, "Available", ""))
			library.commit()
			library.close()
		except:
			result = "There was an error while processing your request, please try again."

		#LOGGING
		LibraryLog = open("LibraryLog.log", "a")
		LibraryLog.writelines(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " : " + self.get_user_name(self.user)+" ADDED BOOK " + title + "\n")
		LibraryLog.close()
		return result

	def showLibrary(self, parameters ):
		result=""
		#SQLLITE CONNECTION
		library = sqlite3.connect('library')
		libraryCurser = library.cursor()

		#SQL MAGIC
		try:
			libraryCurser.execute('''SELECT title, author, owner, checkedOutBy, checkoutDate FROM books''')
		except:
			return "There was an error while processing your request, please try again."
		#DISPLAY QUERY
		counter=0
		for row in libraryCurser.fetchall():
			result += str(counter) + ". Title: " + row[0] + " \n	Author: " + row[1] + " \n	Owner: " + row[2]+ " \n	Checked Out By: " + row[3] + " \n	CheckOut Date: " + row[4]
			counter += 1
		library.close()
		return result

	def editBook(self, parameters):
		fieldREGEX = re.compile('(\".*?\") (\".*?\") (\".*?\")')
		result = "EDIT COMPLETE"

		#SQLLITE CONNECTION
		library = sqlite3.connect('library')
		libraryCurser = library.cursor()

		#PARAMETER PARSING
		try:
			title=fieldREGEX.match(parameters).group(1)
			field=fieldREGEX.match(parameters).group(2)
			update=fieldREGEX.match(parameters).group(3)
		except:
			return "Invalid Parameters\n editbook [\"title\"] [\"field\"] [\"fieldUpdate\"]\n"
		title = self.cleanInput(title)
		field = self.cleanInput(field)
		update = self.cleanInput(update)

		#SQL MAGIC
		try:
			if (field == "author"):
				libraryCurser.execute('''UPDATE books SET author = ? WHERE title = ? ''', (update, title))
			elif (field == "owner"):
				libraryCurser.execute('''UPDATE books SET owner = ? WHERE title = ? ''',
									  (self.get_user_name(update), title))
			elif (field == "title"):
				libraryCurser.execute('''UPDATE books SET title = ? WHERE title = ? ''', (update, title))

			library.commit()
			library.close()
		except:
			result = "There was an error Processing your request, please try again"

		#LOGGING
		LibraryLog = open("LibraryLog.log", "a")
		LibraryLog.writelines(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " : " + self.get_user_name(self.user)+" CHANGED FIELD " + field + " TO " + update + "ON BOOK" + title + "\n")
		LibraryLog.close()
		return result

	def checkoutBook(self,parameters):
		fieldREGEX = re.compile('(\".*?\").*')
		result = "Book Checked Out"

		#SQLLITE CONNECTION
		library = sqlite3.connect('library')
		libraryCurser = library.cursor()

		#PARAMETER PARSING
		try:
			title = fieldREGEX.match(parameters).group(1)
		except:
			return "Invalid Parameters\n checkout [\"title\"]\n"
		title = title.replace("\"", "")

		#SQL MAGIC
		try:
			libraryCurser.execute('''UPDATE books SET checkedOutBy = ? WHERE title = ? ''', (self.user, title))
			libraryCurser.execute('''UPDATE books SET checkoutDate= ? WHERE title = ? ''',
								  (datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"), title))
			library.commit()
			library.close()
		except:
			result = "There was an error while processing your request, please try again"

		#LOGGING
		LibraryLog = open("LibraryLog.log", "a")
		LibraryLog.writelines(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " : " + self.get_user_name(self.user) + " CHECKED OUT " + title + "\n")
		LibraryLog.close()
		return result

	def returnBook(self,parameters):
		fieldREGEX = re.compile('(\".*?\").*')

		#SQLLITE CONNECTION
		library = sqlite3.connect('library')
		libraryCurser = library.cursor()

		#PARAMETER PARSING
		try:
			title = fieldREGEX.match(parameters).group(1)
		except:
			return "Invalid Parameters\n checkout [\"title\"]\n"
		title = title.replace("\"", "")

		#SQL MAGIC
		try:
			libraryCurser.execute('''UPDATE books SET checkedOutBy = ? WHERE title = ? ''', ("AVAILABLE", title))
			libraryCurser.execute('''UPDATE books SET checkoutDate= ? WHERE title = ? ''', ("", title))
			library.commit()
			library.close()
		except:
			result = "There was an error while processing your request, please try again."

		#LOGGING
		LibraryLog = open("LibraryLog.log", "a")
		LibraryLog.writelines(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " : " + self.get_user_name(self.user) + " RETURNED " + title  + "\n")
		LibraryLog.close()
		return result

	def removeBook(self, parameters):
		fieldREGEX = re.compile('(\".*?\").*')
		result = "Book Has Been Removed From the Library"

		#SQLLITE CONNECTION
		library = sqlite3.connect('library')
		libraryCurser = library.cursor()

		# PARAMETER PARSING
		try:
			title = fieldREGEX.match(parameters).group(1)
		except:
			return "Invalid Parameters\n removebook [\"title\"]\n"
		title = title.replace("\"", "")
		# SQL MAGIC
		try:
			libraryCurser.execute('''DELETE FROM books WHERE title = ? ''', (title,))
			library.commit()
			library.close()
		except:
			result = "There was an error processing your request, please try again"

		#LOGGING
		LibraryLog = open("LibraryLog.log", "a")
		LibraryLog.writelines(datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " : " + self.get_user_name(self.user) + " REMOVED " + title  + "\n")
		LibraryLog.close()
		return result

	def help(self, parameters):
		response = "Currently I support the following commands:\r\n"
		
		response +="addbook [\"title\"]\n" \
				   "showlibrary\n" \
				   "editbook [\"title\"] [\"field\"] [\"fieldUpdate\"]\n" \
				   "checkout [\"title\"]\n" \
				   "return [\"title\"]\n" \
				   "remove [\"title\"]\n" \
				   "help"

		return response

	#USES THE SLACK API TO CONVERT USER ID TO USERNAME
	def get_user_name(self, id):
		id = self.cleanInput(id)
		api_call = self.slackCLient.api_call("users.list")
		if api_call.get('ok'):
			# retrieve all users so we can find the user
			users = api_call.get('members')
			for user in users:
				if user.get('id').lower() == id.lower():
					return "<@" + user.get('name') + ">"
			return "ERROR"

	def cleanInput(self,input):
		input = input.replace("\"", "")
		input = input.replace("@", "")
		input = input.replace("<", "")
		input = input.replace(">", "")
		input = input.strip()
		return input