import disnake
import asyncio
import ytdl
from disnake.ext import commands
from typing import Optional
from queue import Queue


class StanVoiceClient(disnake.VoiceClient):

    def __init__(self, client: disnake.Client, channel: disnake.abc.Connectable):

        super().__init__(client, channel)
        self._queue: Queue[ytdl.MediaInfo] = Queue()
        self._current_info: Optional[ytdl.MediaInfo] = None
        self._looping: bool = False
        self._announce_channel: Optional[disnake.TextChannel] = None

    async def enqueue(self, url: str, inter: disnake.ApplicationCommandInteraction):

        self._announce_channel = inter.channel

        await inter.response.defer()

        infos = await ytdl.extract_media_info(url, ytdl.MediaType.Audio)

        for info in infos:
            self._queue.put(info)

        if self.is_playing():
            if len(infos) == 1:
                await inter.send(f"Queued {infos[0].title}")
            else:
                m = "Queued playlist items:\n"
                for info in infos:
                    m += info.title + "\n"
                await inter.send(m)
        else:
            await self.play_next(inter)

            if len(infos) > 1:
                m = "Queued playlist items:\n"
                for info in infos[1:]:
                    m += info.title + "\n"
                await inter.channel.send(m)

    async def play_next(self, inter: Optional[disnake.ApplicationCommandInteraction] = None):

        self.stop()

        info = self._queue.get(block=False)
        self._current_info = info

        source = disnake.FFmpegPCMAudio(info.media_url, **get_ffmpeg_options())
        self.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.on_end(), self.client.loop))
        if inter:
            await inter.send(f"Playing {info.title}...")
        elif self._announce_channel:
            await self._announce_channel.send(f"Playing queued {info.title}...")

    async def on_end(self):

        if self._queue.empty():
            if self._looping and self._current_info:
                self._queue.put(self._current_info)
                await self.play_next()
            else:
                await self.disconnect(force=True)
                if self._announce_channel:
                    await self._announce_channel.send("Returning to Troll HQ...")
        else:
            await self.play_next()

    async def skip(self, inter: Optional[disnake.ApplicationCommandInteraction] = None):

        if inter:
            if self._current_info:
                await inter.send(f"Skipping {self._current_info.title}...")
            else:
                await inter.send("Skipping on your mom's titties...")

        self.stop()

    async def toggle_looping(self, inter: Optional[disnake.ApplicationCommandInteraction] = None):

        self._looping = not self._looping

        if inter:
            await inter.send(f"Looping {'enabled' if self._looping else 'disabled'}...")


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

