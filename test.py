from slackclient import SlackClient
import time

slack_client = SlackClient("xoxb-403303008263-402160290483-prTeUIWAM3hziOyE1rgIOs0N")

api_call = slack_client.api_call("users.list")
if api_call.get('ok'):
	users = api_call.get('members')
	for user in users:
		print (user.get('name'))



if slack_client.rtm_connect(with_team_state=False):
	print ("Successfully connected, listening for events")
	while True:
		print (slack_client.rtm_read())
		
		time.sleep(1)
else:
	print ("Connection Failed")