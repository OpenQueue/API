# -*- coding: utf-8 -*-

from typing import Dict, Tuple
from sqlalchemy.sql import select, and_, or_
from starlette.authentication import AuthenticationError

from OpenQueue.tables import league_table
from OpenQueue.league import League

from .resources import Sessions
from .tables import (
    api_key_table,
    key_scopes_table,
    scopes_table,
    admin_scopes_table
)


async def api_key(key: str
                  ) -> Tuple[League, str, Dict[str, bool]]:
    """Used to validate & get details on api key.

    Parameters
    ----------
    key : str

    Returns
    -------
    League
        League object.
    str
        User ID.
    Dict[str, bool]
        str
            Scope
        bool
            If public scope

    Raises
    ------
    AuthenticationError
    """

    query = select([
        api_key_table.c.league_id,
        api_key_table.c.user_id,
        key_scopes_table.c.public_schema,
        scopes_table.c.scope
    ]).select_from(
        api_key_table.join(
            league_table,
            league_table.c.league_id == api_key_table.c.league_id
        ).join(
            key_scopes_table,
            key_scopes_table.c.api_key == api_key_table.c.api_key
        ).join(
            scopes_table,
            scopes_table.c.scope_id == key_scopes_table.c.scope_id
        )
    ).where(
        and_(
            api_key_table.c.api_key == key,
            or_(
                league_table.c.allow_api_access == True,  # noqa: E712
                league_table.c.user_id == api_key_table.c.user_id
            )
        )
    )

    scopes = {}

    league_id: str = ""
    user_id: str = ""

    async for row in Sessions.database.iterate(query):
        league_id = row["league_id"]
        user_id = row["user_id"]
        scopes[row["scope"]] = row["public_schema"]

    if league_id:
        if "league" not in scopes:
            scopes["league"] = True

        return Sessions.base.league(league_id), user_id, scopes
    else:
        raise AuthenticationError()


async def admin_scopes(user_id: str, league_id: str) -> Dict[str, bool]:
    """Used to get admin scopes.

    Parameters
    ----------
    user_id : str
    league_id : str

    Returns
    -------
    Dict[str, bool]
    """

    query = select([
        admin_scopes_table.c.public_schema,
        scopes_table.c.scope
    ]).select_from(
        admin_scopes_table.join(
            scopes_table,
            scopes_table.c.scope_id == admin_scopes_table.c.scope_id
        )
    ).where(
        and_(
            admin_scopes_table.c.league_id == league_id,
            admin_scopes_table.c.user_id == user_id
        )
    )

    scopes = {}
    async for row in Sessions.database.iterate(query):
        scopes[row["scope"]] = row["public_schema"]

    if scopes:
        scopes["is_admin"] = True

    return scopes
