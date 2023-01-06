import disnake
import asyncio
import ytdl
from disnake.ext import commands
from typing import Optional
from queue import Queue
from datetime import datetime


class StanVoiceClient(disnake.VoiceClient):

    def __init__(self, client: disnake.Client, channel: disnake.abc.Connectable):

        super().__init__(client, channel)
        self._queue: Queue[ytdl.MediaInfo] = Queue()
        self._current_info: Optional[ytdl.MediaInfo] = None
        self._looping: bool = False
        self._embed_message: Optional[disnake.Message] = None
        self._announce_channel: Optional[disnake.TextChannel] = None
        self._last_member: Optional[disnake.Member] = None

    async def enqueue(self, url: str, inter: disnake.ApplicationCommandInteraction) -> None:

        self._announce_channel = inter.channel
        self._last_member = inter.author

        await inter.response.defer()

        infos = await ytdl.extract_media_info(url, ytdl.MediaType.Audio)

        for info in infos:
            self._queue.put(info)

        if not self.is_playing():
            await self.play_next()
        else:
            await self.update_embed()

        await inter.delete_original_message()

    async def play_next(self) -> None:

        self.stop()

        info = self._queue.get(block=False)
        self._current_info = info

        source = disnake.FFmpegPCMAudio(info.media_url, **get_ffmpeg_options())
        self.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.on_end(), self.client.loop))

        await self.send_or_update_embed()

    async def on_end(self) -> None:

        if self._queue.empty():
            if self._looping and self._current_info:
                self._queue.put(self._current_info)
                await self.play_next()
            else:
                await self.clear()
                await self.disconnect()
        else:
            if self._looping and self._current_info:
                self._queue.put(self._current_info)
            await self.play_next()

    async def skip(self, inter: Optional[disnake.ApplicationCommandInteraction] = None, no_loop: bool = False) -> None:

        await inter.send(f"Skipping {self._current_info.title}{' and ignoring looping' if no_loop else ''}...",
                         delete_after=10)
        if no_loop:
            self._current_info = None
        self.stop()
        await self.update_embed()

    async def toggle_looping(self, inter: Optional[disnake.ApplicationCommandInteraction] = None) -> None:

        self._looping = not self._looping
        await self.update_embed()
        text = "enabled" if self._looping else "disabled"
        await inter.send(f"Looping {text}...", delete_after=10)

    async def generate_embed(self) -> disnake.Embed:

        embed = disnake.Embed(
            title="Echoes of the Void",
            color=0x8c041f,
            timestamp=datetime.now()
        )

        if self._last_member is not None:
            embed.set_author(name=self._last_member.nick or self._last_member.name,
                             icon_url=self._last_member.avatar.url)

        if self._current_info is not None:
            embed.add_field("Currently Playing", self._current_info.title, inline=False)
        else:
            embed.add_field("Currently Playing:", "None", inline=False)

        count = 0
        field_content = ""
        l: list[ytdl.MediaInfo] = list(self._queue.queue)
        if len(l) > 0:
            for idx, i in enumerate(l):
                field_content += f"{idx + 1}. {i.title}\n"
        else:
            field_content = "No Queue"

        embed.add_field("Queue:", field_content, inline=False)

        embed.set_footer(text=f"Currently looping:  {self._looping}")

        return embed

    async def send_or_update_embed(self) -> None:

        if self._embed_message is None:
            await self.send_embed()
            return

        if self._embed_message.channel is not self._announce_channel:
            await self._embed_message.delete()
            await self.send_embed()
            return

        await self.update_embed()

    async def update_embed(self) -> None:

        if self._embed_message is None:
            return

        new_embed = await self.generate_embed()
        await self._embed_message.edit(embeds=[new_embed])

    async def send_embed(self) -> None:

        if self._announce_channel is None:
            return

        embed = await self.generate_embed()
        self._embed_message = await self._announce_channel.send(embeds=[embed])

    async def clear(self) -> None:

        await self._embed_message.delete()


def is_connected_to_voice(member: disnake.Member) -> bool:
    return member.voice is not None and member.voice.channel is not None


def try_get_voice_channel(member: disnake.Member) -> Optional[disnake.VoiceChannel]:
    if not is_connected_to_voice(member):
        return None

    return member.voice.channel


def try_get_voice_client(bot: commands.Bot, channel: disnake.VoiceChannel) -> Optional[StanVoiceClient]:
    vc: StanVoiceClient | disnake.VoiceProtocol = disnake.utils.get(bot.voice_clients, channel=channel)

    return vc


async def ensure_in_channel(bot: commands.Bot, channel: disnake.VoiceChannel) -> StanVoiceClient:
    vc = try_get_voice_client(bot, channel)
    if vc is None:
        vc = await channel.connect(reconnect=False, cls=StanVoiceClient)
    elif vc.channel is not channel:
        await vc.move_to(channel)

    return vc


def get_ffmpeg_options(speed: float = 1) -> dict[str, str]:
    speed = round(speed, 2)

    if speed < 0.01:
        speed = 0.01
    elif speed > 10:
        speed = 10

    ffmpeg_options = {
        'options': f'-vn  -filter:a "atempo={speed},atempo={speed}"',
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
    }

    return ffmpeg_options
