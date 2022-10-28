import disnake
import random
import io
from bot import StanBot
from typing import Optional
from datetime import datetime


async def relay_error(bot: StanBot,
                      ex: Exception,
                      message: Optional[disnake.Message] = None):

    owner_id = 188421688453627904
    text = f"I farded with {repr(ex)} at {datetime.today().strftime('%I:%M %p')}"
    if message:
        text += f" in channel:{message.channel.name}."
    else:
        text += "."

    owner = await bot.fetch_user(owner_id)
    await owner.send(text)


def random_chance(percent: float) -> bool:

    n = random.random() * 100.0
    print(n)

    if n <= percent:
        return True
    return False
