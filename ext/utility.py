import disnake
import ytdl
import aiohttp
import io
from disnake.ext import commands
from bot import StanBot


class Utility(commands.Cog):

    def __init__(self, bot: StanBot):
        self.bot = bot

    @commands.slash_command(
        description="Command Stan to rip media files from a url.",
        dm_permission=True
    )
    async def rip(self,
                  inter: disnake.ApplicationCommandInteraction,
                  url: str = commands.Param(description="The url to rip from."),
                  media_type: ytdl.MediaType = commands.Param(description="Type of media to rip.")
                  ):

        await inter.response.defer()

        infos = await ytdl.extract_media_info(url, media_type)
        files = []
        async with aiohttp.ClientSession() as session:
            for info in infos:
                async with session.get(info.media_url) as response:

                    if response.status not in range(200, 300):
                        continue

                    b = await response.read()
                    file = io.BytesIO(b)

                    if len(files) < 10:
                        files.append(disnake.File(file, filename=f"{info.title}.{info.extension}"))

        await inter.send("Ripped files:", files=files)


def setup(bot: StanBot) -> None:
    bot.add_cog(Utility(bot))
