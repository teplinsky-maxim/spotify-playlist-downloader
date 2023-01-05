import abc


class DownloaderBase(abc.ABC):
    def __init__(self):
        ...

    async def download(self, url: str) -> tuple[str, bool]:
        raise NotImplementedError
