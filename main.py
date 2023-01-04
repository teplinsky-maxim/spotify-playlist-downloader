import asyncio

from core.downloader.soundloader.soundloader import SoundLoaderDownloader
from core.playlist.extractor.spotify.spotify import PlaylistExtractor


async def main():
    url = 'https://open.spotify.com/playlist/37i9dQZF1E8OSy3MPBx3OT'

    extractor = PlaylistExtractor()
    songs = await extractor.extract(url)

    downloader = SoundLoaderDownloader()
    for song in songs:
        result = await downloader.download(song)
        print(f'{song} -> {result}')

if __name__ == '__main__':
    asyncio.run(main())
