import disnake
import utils
from disnake.ext import commands
from bot import StanBot
from language import tags


class Base(commands.Cog):
    def __init__(self, bot: StanBot):
        self.bot = bot

    @commands.slash_command(
        description="Command Stan to kill himself.",
        dm_permission=True
    )
    async def restart(self,
                      inter:disnake.ApplicationCommandInteraction
                      ):

        if not utils.is_admin(inter.author):
            await inter.send("Ballsack denied.", delete_after=10)
            return

        await inter.send("Restarting...", delete_after=10)
        exit()

    @commands.slash_command(
        description="Ask Stan to imbue text with sussiness.",
        dm_permission=True
    )
    async def sussify(self,
                      inter: disnake.ApplicationCommandInteraction,
                      text: str = commands.Param(description="The text to rape.")
                      ):

        await inter.response.defer()

        try:
            result = tags.replace_words_by_tag_random(text).replace("  ", "\n")
            if len(result) < 2001:
                await inter.send(result)
            else:
                await inter.send("Result over 2000 characters, initiating poop dispenser:")
                it = [result[i:min(i+2000, len(result))] for i in range(0, len(result), 2000)]
                for i in it:
                    await inter.channel.send(i)
        except Exception as e:
            await inter.send("I farded.", delete_after=10)
            await utils.relay_error(self.bot, e, await inter.original_message())

    @commands.message_command(
        name="Sussify Message",
        description="Ask Stan to imbue text with sussiness.",
        dm_permission=True
    )
    async def sussify_selected(self, inter: disnake.ApplicationCommandInteraction):

        if not inter.target or len(inter.target.content) < 1:
            await inter.send("I can't sussify that, retard.", delete_after=10)
            return

        await self.sussify(inter, inter.target.content)

    @commands.slash_command(
        description="Change Stan's activity.",
        dm_permission=True
    )
    async def set_activity(self,
                           inter: disnake.ApplicationCommandInteraction,
                           activity_name: str = commands.Param(description="The name of the activity to display."),
                           activity_type: disnake.ActivityType = commands.param(description="The type of activity.")
                           ):

        try:
            activity = disnake.Activity(name=activity_name, type=activity_type)
            await self.bot.change_presence(activity=activity)
            await inter.send(f"Activity set to '{activity_name}'.")
        except Exception as e:
            await inter.send("I farded", delete_after=10)
            await utils.relay_error(self.bot, e, await inter.original_message())


def setup(bot: StanBot) -> None:
    bot.add_cog(Base(bot))
