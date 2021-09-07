# -*- coding: utf-8 -*-

from typing import List


class ApiSettings:
    def __init__(self, root_users: List[str] = [],
                 league_scope: str = "league.") -> None:
        """Scope leagues are allowed to assign.

        Parameters
        ----------
        root_users : List[str], optional
            NL user ID, by default []
        league_scope : str, optional
            by default "league."
        """

        self.root_users = root_users
        self.league_scope = league_scope
