import abc
from typing import Iterable


class PlaylistExtractorBase(abc.ABC):
    def __init__(self):
        ...

    async def extract(self, url: str) -> Iterable[str]:
        raise NotImplementedError
