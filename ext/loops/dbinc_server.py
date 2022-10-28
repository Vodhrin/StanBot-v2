import disnake
import json
from typing import Optional
from loop_act import LoopAction
from bot import StanBot


class DBIncServerLoop(LoopAction):

    def __init__(self, bot: StanBot):

        super().__init__(bot)
        self.guild_id = 575069828646174736
        self.guild: Optional[disnake.Guild] = None

    async def execute(self):

        if self.guild is None:
            self.guild = await self.bot.fetch_guild(self.guild_id)


def setup(bot: StanBot):
    bot.add_loop(DBIncServerLoop(bot))
