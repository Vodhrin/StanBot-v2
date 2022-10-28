import disnake
import json

PREFIX = "%"
INTENTS = disnake.Intents.all()
TOKENS = json.load(open("tokens"))
