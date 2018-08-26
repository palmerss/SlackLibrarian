import command
import re

class Event:
	def __init__(self, bot):
		self.bot = bot
		self.command = command.Command()
	
	def wait_for_event(self):
		events = self.bot.slack_client.rtm_read()
		
		if events and len(events) > 0:
			for event in events:
				#print event
				self.parse_event(event)
				
	def parse_event(self, event):
		if event and 'text' in event:
			self.handle_event(event['user'], event['text'].strip(), event['channel'])
	
	def handle_event(self, user, command, channel):
		#when a slack message is sent it triggers an event, even if it is the bot replying, this block allows us to check if the bot is replying.
		if(self.bot.get_bot_id() == "<@"+user+">"):
			return
		if command and channel:
			print ("Received command: " + command + " in channel: " + channel + " from user: " + user)
			response = self.command.handle_command(user, command, self.bot.slack_client)
			self.bot.slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
