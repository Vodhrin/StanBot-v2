import yt_dlp
import asyncio
from dataclasses import dataclass
from enum import Enum

yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options_audio = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    'cookiefile': 'cookies.txt',
    'cachedir': False
}
ytdl_format_options_video = {
    'format': 'best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    'cookiefile': 'cookies.txt',
    'cachedir': False
}


ytdl_audio = yt_dlp.YoutubeDL(ytdl_format_options_audio)
ytdl_video = yt_dlp.YoutubeDL(ytdl_format_options_video)


class MediaType(Enum):
    Audio = 0
    Video = 1


@dataclass
class MediaInfo:
    title: str
    page_url: str
    media_url: str
    extension: str
    media_type: MediaType


async def extract_media_info(url: str, media_type: MediaType) -> [MediaInfo]:

    loop = asyncio.get_event_loop()
    if media_type is MediaType.Audio:
        data = await loop.run_in_executor(None, lambda: ytdl_audio.extract_info(url, download=False))
    else:
        data = await loop.run_in_executor(None, lambda: ytdl_video.extract_info(url, download=False))

    infos = []

    if "entries" in data:
        for entry in data["entries"]:
            info = MediaInfo(entry["title"],
                             entry["webpage_url"],
                             entry["url"],
                             entry["ext"],
                             MediaType.Audio if "audio only" in entry["format"] else MediaType.Video)
            infos.append(info)
        return infos

    info = MediaInfo(data["title"],
                     data["webpage_url"],
                     data["url"],
                     data["ext"],
                     MediaType.Audio if "audio only" in data["format"] else MediaType.Video)
    infos.append(info)
    return infos


# async def download_media(url: str, media_type: MediaType) -> io.BytesIO:
#
#     ext_loops = asyncio.get_event_loop()
#     if media_type is MediaType.Audio:
#         data = await ext_loops.run_in_executor(None, lambda: ytdl_audio.download())
#     else:
#         data = await ext_loops.run_in_executor(None, lambda: ytdl_video.extract_info(url, download=False))
