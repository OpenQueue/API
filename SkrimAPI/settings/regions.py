# -*- coding: utf-8 -*-


from typing import Dict, List


class Region:
    def __init__(self, roles: List[int], league_id: str) -> None:
        """
        Parameters
        ----------
        roles : List[int]
            List of role snowflake IDs.
        league_id : str
        """

        self.roles = roles
        self.league_id = league_id


class RegionSettings:
    def __init__(self, regions: Dict[str, Region],
                 guild_id: int,
                 roles: List[int] = None,
                 fallback: str = "GB") -> None:
        """Configure regions.

        Parameters
        ----------
        regions : Dict[str, Region]
        guild_id : int
            Guild ID
        roles : List[int]
            List of role snowflake IDs to apply to all regions.
        fallback : str, optional
            by default "GB"
        """

        assert fallback in regions

        self.regions = {key.upper(): value for key, value in regions.items()}
        self.roles = roles
        self.fallback = fallback.upper()
        self.guild_id = guild_id
