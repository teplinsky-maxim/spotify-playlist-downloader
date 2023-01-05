import argparse
import asyncio
import time

from core.downloader.soundloader.soundloader import SoundLoaderDownloader
from core.logger.main import Logger
from core.playlist.extractor.spotify.spotify import PlaylistExtractor


async def process(playlist: str, directory_to_save: str, threads: int) -> None:
    tb = time.time()
    extractor = PlaylistExtractor()
    print(f'Extracting from {playlist} ...')
    songs = await extractor.extract(playlist)
    songs = songs[20:]
    total_songs = len(songs)
    print(f'... {total_songs} songs found')

    downloader = SoundLoaderDownloader(directory_to_save)
    futures = set()

    ok = 0
    failed = 0
    while len(songs):
        while len(futures) < threads and len(songs) != 0:
            futures.add(asyncio.create_task(downloader.download(songs[0])))
            songs = songs[1:]
        return_when = asyncio.FIRST_COMPLETED if len(songs) != 0 else asyncio.ALL_COMPLETED
        print(return_when)
        done, _ = await asyncio.wait(futures, return_when=return_when)
        for item in done:
            url, result = item.result()
            if item.done():
                if result is True:
                    ok = ok + 1
                else:
                    failed = failed + 1
                Logger.song_store(url, result)
            else:
                Logger.song_store(url, False)
            Logger.total(total_songs, ok, failed)
            futures.remove(item)

    Logger.total(time.time() - tb)


async def main():
    parser = argparse.ArgumentParser(description='Download playlists from spotify')
    parser.add_argument('playlist', type=str, help='URL to playlist. Example: https://open.spotify.com/playlist/37i9dQZF1E8OSy3MPBx3OT')
    parser.add_argument('-d', '--dir', type=str, default='.', help='Path to store tracks', required=False)
    parser.add_argument('-t', '--threads', type=int, default=5, help='Amount of tracks to store at the same time. '
                                                                     'Please, be careful with that option, high numbers may cause '
                                                                     'problems on the service we use under the hood, do not let it down', required=False)
    args = parser.parse_args()

    await process(args.playlist, args.dir, args.threads)


if __name__ == '__main__':
    asyncio.run(main())
