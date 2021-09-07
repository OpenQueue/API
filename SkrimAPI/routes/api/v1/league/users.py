# -*- coding: utf-8 -*-

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.authentication import requires
from starlette.responses import JSONResponse

from webargs import fields
from webargs_starlette import use_args

from ....response import response
from ....decorators import required_states


class LeagueUsersAPI(HTTPEndpoint):
    @use_args({"search": fields.Str(), "page": fields.Int(),
               "desc": fields.Bool()})
    @requires("league.users")
    @required_states("league")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Lists user for a league.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        league = request.state.league
        public_schema = request.state.public_schema["league.matches"]

        data = [
            player.api_schema(public_schema)
            async for player, _ in league.players(**paramters)
        ]

        return response(data)
