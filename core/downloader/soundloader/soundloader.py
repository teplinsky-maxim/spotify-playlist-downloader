import asyncio
import time

from aiohttp import ClientSession
import aiofiles

from core.downloader.base import DownloaderBase
from core.logger.main import Logger


class SoundLoaderDownloader(DownloaderBase):
    def __init__(self, path_to_tracks: str):
        super().__init__()
        self._path_to_tracks = path_to_tracks

    async def download(self, url: str) -> tuple[str, bool]:
        track_metadata, etag = await self._fetch_metadata_request(url)
        downloader_metadata, etag = await self._start_download(track_metadata)
        track_id = downloader_metadata['id']
        path = await self._wait_until_track_is_available(url, track_id)
        if path is None:
            return url, False
        Logger.storing(url)
        await self._download_track(path)
        return url, True

    async def _download_track(self, path: str) -> None:
        name = path.split('/')[-1]
        headers = self._get_headers('audio/mpeg')

        async with ClientSession() as session:
            async with session.get(path, headers=headers) as resp:
                f = await aiofiles.open(f'{self._path_to_tracks}/{name}', mode='wb')
                await f.write(await resp.read())
                await f.close()

    async def _get_download_path(self, track_id: str, etag: str) -> tuple[dict | None, str]:
        url = f'https://api.soundloaders.com/download/check/{track_id}'

        headers = self._get_headers(etag=etag)

        params = {
            'type': 'track'
        }

        async with ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                if resp.status == 304:
                    return None, etag
                data = await resp.json()

                etag = resp.headers['etag']

                return data, etag

    async def _wait_until_track_is_available(self, url: str, track_id: str, max_seconds_to_wait: int = 300) -> str | None:
        path_to_download = None
        tb = time.time()
        etag = None
        while time.time() <= tb + max_seconds_to_wait:
            data, etag = await self._get_download_path(track_id, etag)
            if data is None:
                await asyncio.sleep(2)
                continue

            queue_position = data.get('position', None)
            if queue_position is not None:
                Logger.queue_position(url, queue_position)
                await asyncio.sleep(2)
                continue

            path_to_download = data['data'].get('path', None)
            if path_to_download is None:
                await asyncio.sleep(2)
                continue

            break
        return path_to_download

    async def _start_download(self, metadata: dict) -> tuple[dict, str]:
        url = 'https://api.soundloaders.com/download/track'

        headers = self._get_headers('application/json')

        json_data = {
            'downloader': 'spotify',
            'metadata': metadata
        }

        async with ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as resp:
                data = await resp.json()

                etag = resp.headers['etag']

                return data, etag

    async def _fetch_metadata_request(self, song_url: str) -> tuple[dict, str]:
        url = 'https://api.soundloaders.com/spotify/track'

        headers = self._get_headers()

        params = {
            'url': song_url
        }

        async with ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()

                etag = resp.headers['etag']

                return data, etag

    @staticmethod
    def _get_headers(content_type: str | None = None, etag: str | None = None):
        base_headers = {
            'authority': 'api.soundloaders.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,kk;q=0.5',
            'authorization': 'Basic bjZfLUg3eDJuc2VVcUhOcG9DY2FNS2dmOk5oVVA0NyFRc0NKeUhzSnhUblZtLkJWaw==',
            'dnt': '1',
            'origin': 'https://www.soundloaders.com',
            'referer': 'https://www.soundloaders.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }

        if etag is not None:
            base_headers['if-none-match'] = etag

        if content_type is not None:
            base_headers['content-type'] = content_type

        return base_headers
