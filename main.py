import argparse
import asyncio

from core.downloader.soundloader.soundloader import SoundLoaderDownloader
from core.playlist.extractor.spotify.spotify import PlaylistExtractor


async def main():
    parser = argparse.ArgumentParser(description='Download playlists from spotify')
    parser.add_argument('playlist', type=str, help='URL to playlist. Example: https://open.spotify.com/playlist/37i9dQZF1E8OSy3MPBx3OT')
    parser.add_argument('-d', '--dir', type=str, default='.', help='Path to store tracks', required=False)
    parser.add_argument('-t', '--threads', type=int, default=1, help='Amount of tracks to store at the same time', required=False)
    args = parser.parse_args()

    extractor = PlaylistExtractor()
    print(f'Extracting from {args.playlist} ...')
    songs = await extractor.extract(args.playlist)
    print(f'... {len(songs)} songs found')

    downloader = SoundLoaderDownloader(args.dir)
    futures = set()

    while len(songs):
        while len(futures) < args.threads and len(songs) != 0:
            futures.add(asyncio.create_task(downloader.download(songs[0])))
            songs = songs[1:]
        done, _ = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
        for item in done:
            if item.done():
                if item.result() is True:
                    print('ok')
            print('not ok')
            futures.remove(item)


if __name__ == '__main__':
    asyncio.run(main())
