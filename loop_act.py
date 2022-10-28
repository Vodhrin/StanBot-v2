from disnake.ext.commands import Bot
from abc import ABC, abstractmethod


class LoopAction(ABC):

    def __init__(self, bot: Bot):
        self.bot: Bot = bot

    @abstractmethod
    async def execute(self):
        pass
