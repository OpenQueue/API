# -*- coding: utf-8 -*-

from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import JSONResponse

from webargs import fields
from webargs_starlette import use_args

from ...response import response
from ...decorators import required_states

from ....misc import SkrimRequest


class UserAPI(HTTPEndpoint):
    @requires("user")
    @required_states(["site.loggedIn", "user"])
    async def get(self, request: SkrimRequest) -> JSONResponse:
        """Used to get User data.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        user = request.state.user
        public_schema = request.state.public_schema["user"]

        return response((await user.get()).api_schema(public_schema))

    @use_args({"league_id": fields.String(required=True, min=2, max=6),
               "league_name": fields.String(required=True, min=3, max=32),
               "region": fields.String(min=1, max=20),
               "email": fields.Email(required=True),
               "anticheat": fields.Boolean(),
               "allow_api_access": fields.Boolean(),
               "kill": fields.Float(), "death": fields.Float(),
               "round_won": fields.Float(), "round_lost": fields.Float(),
               "match_won": fields.Float(), "match_lost": fields.Float(),
               "assist": fields.Float(), "mate_blinded": fields.Float(),
               "mate_killed": fields.Float()})
    @requires(["site.loggedIn", "user.owner"])
    @required_states("user")
    async def post(self, request: SkrimRequest, paramters: dict
                   ) -> JSONResponse:
        """Used to create league.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        model, _ = await request.state.user.create_league(**paramters)
        request.session["login"]["league_ids"].append(model.league_id)

        return response(model.api_schema(
            request.state.public_schema["user.owner"]
        ))
