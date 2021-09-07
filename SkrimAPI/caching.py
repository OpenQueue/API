# -*- coding: utf-8 -*-

"""
Currently we only cache league data.
Global data is only used by us, so wont
be under the same amount of stress.
"""

from typing import Any
from .resources import Sessions


class CacheBase:
    def __init__(self, key: str) -> None:
        """Used to cache something.

        Parameters
        ----------
        key : str
        """

        self.key = key

    async def delete(self) -> None:
        await Sessions.cache.delete(self.key)

    async def set(self, value: Any, ttl=180) -> None:
        await Sessions.cache.set(self.key, value, ttl=ttl)

    async def get(self) -> Any:
        return await Sessions.cache.get(self.key)

    async def exists(self) -> bool:
        return await Sessions.cache.exists()


class CacheMatch(CacheBase):
    def __init__(self, league_id: str, match_id: str) -> None:
        super().__init__("league-" + league_id + "-match-" + match_id)


class CacheScoreboard(CacheBase):
    def __init__(self, league_id: str, match_id: str) -> None:
        super().__init__("league-" + league_id + "-scoreboard-" + match_id)


class CacheMatches(CacheBase):
    def __init__(self, league_id: str) -> None:
        super().__init__("league-" + league_id + "-matches")


class CacheUser(CacheBase):
    def __init__(self, league_id: str, user_id: str) -> None:
        super().__init__(
            "league-" + league_id + "-user-" + user_id,
        )


class CacheAPIKey(CacheBase):
    def __init__(self, api_key: str) -> None:
        super().__init__("api-key-" + api_key)
