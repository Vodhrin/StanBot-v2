import config
from disnake.ext import commands, tasks
from typing import List


class StanBot(commands.Bot):

    def __init__(
            self,
            command_prefix=config.PREFIX,
            intents=config.INTENTS,
            sync_commands_debug=True,
            ):

        super().__init__(command_prefix=command_prefix, intents=intents, sync_commands_debug=sync_commands_debug)
        self.dev: bool = config.IS_DEV


stan_bot = StanBot()
stan_bot.load_extension("ext.base")
stan_bot.load_extension("ext.jukebox")
stan_bot.load_extension("ext.utility")