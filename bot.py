import config
from loop_act import LoopAction
from disnake.ext import commands, tasks
from typing import List


class StanBot(commands.Bot):

    def __init__(
            self,
            command_prefix=config.PREFIX,
            intents=config.INTENTS,
            sync_commands_debug=True
            ):

        super().__init__(command_prefix=command_prefix, intents=intents, sync_commands_debug=sync_commands_debug)
        self._loops: List[LoopAction] = []
        self._execute_loops.start()

    @tasks.loop(seconds=1)
    async def _execute_loops(self):

        for loop in self._loops:
            await loop.execute()

    def add_loop(self, loop: LoopAction):

        if loop not in self._loops:
            self._loops.append(loop)


stan_bot = StanBot()
stan_bot.load_extension("ext.base")
stan_bot.load_extension("ext.jukebox")
stan_bot.load_extension("ext.utility")
stan_bot.load_extension("ext.loops.dbinc_server")
