import asyncio
import random

from aiohttp import ClientSession
import aiofiles

from core.downloader.base import DownloaderBase


class SoundLoaderDownloader(DownloaderBase):
    def __init__(self, path_to_tracks: str):
        super().__init__()
        self._path_to_tracks = path_to_tracks

    async def download(self, url: str) -> bool:
        track_metadata = await self._fetch_metadata_request(url)
        downloader_metadata = await self._start_download(track_metadata)
        track_id = downloader_metadata['id']

        max_tries = 5
        tries = 0
        path_to_download = None
        while max_tries >= tries:
            tries = tries + 1

            path_to_download = await self._get_download_path(track_id)
            if path_to_download is None:
                await asyncio.sleep(2 * tries)
                continue
            break
        if path_to_download is None:
            return False
            # raise DownloaderInternalError('No path to download was generated')

        await self._download_track(path_to_download)
        return True

    async def _download_track(self, path: str) -> None:
        name = path.split('/')[-1]

        headers = {
            'authority': 'api.soundloaders.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,kk;q=0.5',
            'dnt': '1',
            'if-modified-since': 'Tue, 06 Dec 2022 05:08:23 GMT',
            'if-none-match': 'W/"9b01b7-184e5d5c558"',
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

        async with ClientSession() as session:
            async with session.get(path, headers=headers) as resp:
                f = await aiofiles.open(f'{self._path_to_tracks}/{name}', mode='wb')
                await f.write(await resp.read())
                await f.close()

    @staticmethod
    async def _get_download_path(track_id: str) -> str | None:
        url = f'https://api.soundloaders.com/download/check/{track_id}'

        headers = {
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

        params = {
            'type': 'track'
        }

        async with ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                try:
                    return data['data']['path']
                except KeyError:
                    return None

    @staticmethod
    async def _start_download(metadata: dict) -> dict:
        url = 'https://api.soundloaders.com/download/track'

        headers = {
            'authority': 'api.soundloaders.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,kk;q=0.5',
            'authorization': 'Basic bjZfLUg3eDJuc2VVcUhOcG9DY2FNS2dmOk5oVVA0NyFRc0NKeUhzSnhUblZtLkJWaw==',
            'content-type': 'application/json',
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

        json_data = {
            'downloader': 'spotify',
            'metadata': metadata
        }

        async with ClientSession() as session:
            async with session.post(url, json=json_data, headers=headers) as resp:
                data = await resp.json()
                return data

    # need to store e-tag from server response
    # at fetch_metadata_request
    # and refactor headers to common

    @staticmethod
    async def _fetch_metadata_request(song_url: str) -> dict:
        url = 'https://api.soundloaders.com/spotify/track'

        headers = {
            'authority': 'api.soundloaders.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,bg;q=0.6,kk;q=0.5',
            'authorization': 'Basic bjZfLUg3eDJuc2VVcUhOcG9DY2FNS2dmOk5oVVA0NyFRc0NKeUhzSnhUblZtLkJWaw==',
            'dnt': '1',
            'if-none-match': 'W/"1c1-H+3Pd7aZB0z+ZNTAsi5PBofCSRw"',
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

        params = {
            'url': song_url
        }

        async with ClientSession() as session:
            async with session.get(url, params=params, headers=headers) as resp:
                data = await resp.json()
                return data
