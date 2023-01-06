from enum import Enum
from dataclasses import dataclass
from typing import Optional


class MediaType(Enum):
    Audio = 0
    Video = 1


@dataclass
class MediaInfo:
    title: str
    page_url: str
    media_url: str
    extension: str
    extractor: str
    thumbnail: Optional[str]
    media_type: MediaType
