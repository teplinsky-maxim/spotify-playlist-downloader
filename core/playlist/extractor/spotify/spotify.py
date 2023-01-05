import re
from typing import Iterable

from aiohttp import ClientSession

from core.playlist.extractor.base import PlaylistExtractorBase


class PlaylistExtractor(PlaylistExtractorBase):
    _SONG_REGEX = re.compile(r'<meta name="music:song" content="(.*?)"/>')

    def __init__(self):
        super().__init__()

    async def extract(self, url: str) -> list[str]:
        page = await self._fetch_page(url)
        songs = self._extract_songs(page)
        return songs

    @staticmethod
    async def _fetch_page(url: str) -> str:
        async with ClientSession() as session:
            async with session.get(url) as resp:
                html = await resp.text()
                return html

    def _extract_songs(self, data: str) -> list[str]:
        # TODO: fix extracting only the first 30 songs
        songs = re.findall(self._SONG_REGEX, data)
        return songs
