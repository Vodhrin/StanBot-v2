import disnake
import json
import os

PREFIX = "%"
INTENTS = disnake.Intents.all()
TOKENS = json.load(open("tokens.json"))

ADMIN_IDS = [int(i.strip()) for i in open("admins.txt").readlines()]

IS_DEV = os.getlogin() == "samco"
