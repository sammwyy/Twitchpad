import socket
import pyautogui
import threading
import yaml
import io

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

SERVER = cfg['Server']['IP']
PORT = cfg['Server']['PORT']
OWNER = cfg['Login']['Username']
PASS = cfg['Login']['OAuth']
CHANNEL = cfg['Login']['Channel']
BOT = "TwitchBot"

KEYS = cfg['Keys']
send_msg_on_join = cfg['Extensions']['msg on join']['enabled']
msg_on_join = cfg['Extensions']['msg on join']['message']


message = ""

print('')
print('  _______       _ _       _     _____          _ ')
print(' |__   __|     (_) |     | |   |  __ \        | |')
print('    | |_      ___| |_ ___| |__ | |__) |_ _  __| |')
print('    | \ \ /\ / / | __/ __| |_ \|  ___/ _` |/ _` |')
print('    | |\ V  V /| | |_|(__| | | | |  | (_| | (_| |')
print('    |_| \_/\_/ |_|\__\___|_| |_|_|   \__,_|\__,_|')
print('')
print('      TwitchPad by https://www.2l-studios.com    ')
print('')

irc = socket.socket()
irc.connect((SERVER, PORT))
irc.send((  "PASS " + PASS + "\n" +
			"NICK " + BOT + "\n" + 
			"JOIN #" + CHANNEL + "\n").encode())

print(cfg['Messages']['logging'])
def gamecontrol(message, user):
	for key in KEYS:
		if key in message.lower():
			msg1 = cfg['Extensions']['show keys in console']['message']
			print(msg1.replace('%key%', message).replace('%user%', user))
			pyautogui.keyDown(key)
			message = ""
			pyautogui.keyUp(key)

def joinChat():
	Loading = True
	while Loading:
		readbuffer_join = irc.recv(1024)
		readbuffer_join = readbuffer_join.decode()
		for line in readbuffer_join.split("\n")[0:-1]:
			Loading = loadingComplete(line)

def loadingComplete(line):
	if ("End of /NAMES list" in line):
		print(cfg['Messages']['succefull_login'])
		if send_msg_on_join:
			sendMessage(irc, msg_on_join)
		return False
	else:
		return True

def sendMessage(irc, message):
	messageTemp = "PRIVMSG #" + CHANNEL + " :" + message
	irc.send((messageTemp + "\n").encode())

def getUser(line):
	separate = line.split(":", 2)
	user = separate[1].split("!", 1)[0]
	return user

def getMessage(line):
	global message
	try:
		message = (line.split(":",2))[2]
	except:
		message = ""
	return message

def Console(line):
	if "PRIVMSG" in line:
		return False
	else:
		return True

joinChat()

print("")

while True:
	try:
		readbuffer = irc.recv(1024).decode()
	except:
		readbuffer = ""
	for line in readbuffer.split("\r\n"):
		if line == "":
			continue
		elif "PING" in line and Console(line):
			msgg = "PONG tmi.twitch.tvrr\r\n".encode()
			irc.send(msgg)
			print(msgg)
			continue
		else:
			user = getUser(line)
			message = getMessage(line)
			gamecontrol(message, user)