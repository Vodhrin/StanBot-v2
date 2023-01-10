import disnake
import random
from bot import StanBot
from config import ADMIN_IDS
from typing import Optional
from datetime import datetime


async def relay_error(bot: StanBot,
                      ex: Exception,
                      message: Optional[disnake.Message] = None):

    text = f"I farded with {repr(ex)} at {datetime.today().strftime('%I:%M %p')}"
    if message:
        text += f" in channel:{message.channel.name}."
    else:
        text += "."

    owner = await bot.fetch_user(ADMIN_IDS[0])
    await owner.send(text)


def is_admin(user: disnake.User):

    return user.id in ADMIN_IDS


def random_chance(percent: float) -> bool:

    n = random.random() * 100.0
    print(n)

    if n <= percent:
        return True
    return False


def trim(string: str, length: int, ellipses: bool = True):

    return (string[:length] + "..." if ellipses else "") if len(string) > length else string