# -*- coding: utf-8 -*-

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.authentication import requires
from starlette.responses import JSONResponse

from OpenQueue.settings.ban import BanSettings

from webargs import fields
from webargs_starlette import use_args

from ....response import response
from ....decorators import required_states

from .....caching import CacheUser


class LeagueUserAPI(HTTPEndpoint):
    @requires("league.user")
    @required_states("user")
    async def get(self, request: Request) -> JSONResponse:
        """Used to get User data within league context.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        user = request.state.user
        public_schema = request.state.public_schema["league.user"]

        cache = CacheUser(
            user.upper.league_id, user.user_id
        )

        cache_get = await cache.get()
        if cache_get:
            return response(cache_get)

        return response((await user.get()).api_schema(public_schema))


class LeagueUserMatchesAPI(HTTPEndpoint):
    @use_args({"search": fields.Str(), "page": fields.Int(),
               "desc": fields.Bool()})
    @requires("league.user.matches")
    @required_states("user")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Used to get User matches within league context.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        user = request.state.user
        public_schema = request.state.public_schema["league.user.matches"]

        return response([
            match.api_schema(public_schema)
            async for match, _ in user.matches(**paramters)
        ])


class LeagueUserBanAPI(HTTPEndpoint):
    @requires("league.user.ban")
    @required_states("ban")
    async def get(self, request: Request) -> JSONResponse:
        """Used to get details on a ban.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        return response(
            (await request.state.ban.get()).api_schema(
                request.state.public_schema["league.user.ban"]
            )
        )

    @requires("league.user.ban.exception")
    @required_states("ban")
    async def delete(self, request: Request) -> JSONResponse:
        """Used to make a exception for a global ban.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        await request.state.ban.league_exception()
        return response()

    @requires("league.user.ban.revoke")
    @required_states("ban")
    async def patch(self, request: Request) -> JSONResponse:
        """Used to revoke a ban.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        await request.state.ban.revoke()
        return response()

    @use_args({"reason": fields.String(required=True),
               "expires": fields.DateTime(required=True),
               "banner_id": fields.String(required=True, min=36, max=36)})
    @requires("league.user.create_ban")
    @required_states("user")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Used to ban user.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        return response(
            (await request.state.user.create_ban(
                BanSettings(**paramters)
            )).api_schema(
                request.state.public_schema["league.user.create_ban"]
            )
        )
