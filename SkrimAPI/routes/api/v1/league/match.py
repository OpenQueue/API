# -*- coding: utf-8 -*-

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.authentication import requires
from starlette.responses import JSONResponse

from marshmallow import Schema, validate
from webargs import fields
from webargs_starlette import use_args

from OpenQueue.league import League
from OpenQueue.settings.match import MatchSettings

from ....response import response, error_response
from ....decorators import required_states

from .....caching import (
    CacheScoreboard,
    CacheMatch
)


class TeamSchema(Schema):
    name = fields.String(required=True, max=64)
    players = fields.List(
        fields.String(min=36, max=36),
        validates=validate.Length(1, 30)
    )
    captain = fields.String(min=36, max=36)


MATCH_FIELDS = {
    "team_1": fields.Nested(TeamSchema, required=True),
    "team_2": fields.Nested(TeamSchema, required=True),
    "players": fields.List(
        fields.String(min=36, max=36),
        validates=validate.Length(1, 30)
    ),
    "maps": fields.List(
        fields.String(required=True, max=24),
        required=True,
        validates=validate.Length(1, 120)
    ),
    "connection_time": fields.Integer(missing=300),
    "knife_round": fields.Bool(missing=False),
    "wait_for_spectators": fields.Bool(missing=False),
    "warmup_time": fields.Integer(missing=15)
}


class PlayersSchema(Schema):
    name = fields.String(min=1, max=42, required=True)
    user_id = fields.String(min=36, max=36, required=True)
    team = fields.Int(required=True)
    alive = fields.Bool(required=True)
    ping = fields.Int(required=True)
    kills = fields.Int(required=True)
    headshots = fields.Int(required=True)
    assists = fields.Int(required=True)
    deaths = fields.Int(required=True)
    shots_fired = fields.Int(required=True)
    shots_hit = fields.Int(required=True)
    mvps = fields.Int(required=True)
    score = fields.Int(required=True)
    disconnected = fields.Bool(required=True)
    team_blinds = fields.Int(required=True)
    team_kills = fields.Int(required=True)


class LeagueMatchCreateAPI(HTTPEndpoint):
    @use_args(MATCH_FIELDS)
    @requires("league.create_match")
    @required_states("league")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Used to create a match.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        league: League = request.state.league

        match_settings = MatchSettings(
            team_1_name=paramters["team_1"]["name"],
            team_2_name=paramters["team_2"]["name"],
            connection_time=paramters["connection_time"],
            knife_round=paramters["knife_round"],
            wait_for_spectators=paramters["wait_for_spectators"],
            warmup_time=paramters["warmup_time"]
        )

        map_selection = request.path_params["map_selection"].lower()
        if map_selection == "random":
            match_settings.maps(paramters["maps"]).random()
        elif map_selection == "given":
            match_settings.maps(paramters["maps"]).given()
        else:
            return error_response("Invalid map selection type")

        player_selection = request.path_params["player_selection"].lower()
        if player_selection == "given":
            if ("players" not in paramters["team_1"]
                    or "players" not in paramters["team_2"]):
                return error_response("Players not given for both teams")

            await match_settings.players().given(
                team_1=paramters["team_1"]["players"],
                team_2=paramters["team_2"]["players"]
            )

        elif player_selection == "random":
            if "players" not in paramters:
                return error_response("Players not given")

            await match_settings.players().random(paramters["players"])

        elif player_selection == "elo":
            if "players" not in paramters:
                return error_response("Players not given")

            await match_settings.players().elo(paramters["players"])

        else:
            return error_response("Invalid player selection type")

        captain_selection = request.path_params["captain_selection"].lower()
        if captain_selection == "given":
            if ("captain" not in paramters["team_1"]
                    or "captain" not in paramters["team_2"]):
                return error_response("Captains not given")

            match_settings.captains().given(
                captain_1=paramters["team_1"]["captain"],
                captain_2=paramters["team_2"]["captain"]
            )

        elif captain_selection == "random":
            match_settings.captains().random()
        elif captain_selection == "elo":
            match_settings.captains().elo()
        else:
            return error_response("Invalid captain selection")

        scoreboard, _, _ = await league.create_match(match_settings)

        return response(scoreboard.api_schema(
            request.state.public_schema["league.create_match"]
        ))


class LeagueMatchAPI(HTTPEndpoint):
    @requires("league.match")
    @required_states("match")
    async def get(self, request: Request) -> JSONResponse:
        """Used to get match details.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        match = request.state.match
        public_schema = request.state.public_schema["league.match"]

        cache = CacheMatch(match.upper.league_id, match.match_id)

        cache_get = await cache.get()
        if cache_get:
            return response(cache_get)

        return response((await match.get()).api_schema(public_schema))

    @use_args({"team_1_score": fields.Int(
                required=True, validates=validate.Range(0, 640)
               ),
               "team_2_score": fields.Int(
                   required=True, validates=validate.Range(0, 640)
                ),
               "team_1_side": fields.Int(
                   required=True, validates=validate.Range(0, 1)
                ),
               "team_2_side": fields.Int(
                   required=True, validates=validate.Range(0, 1)
                ),
               "team_1_name": fields.Int(validates=validate.Length(1, 64)),
               "team_2_name": fields.Int(validates=validate.Length(1, 64)),
               "players": fields.List(
                   fields.Nested(PlayersSchema),
                   validates=validate.Length(1, 30)
                )})
    @requires("league.match.update")
    @required_states("match")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Used to update a match.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        match = request.state.match
        public_schema = request.state.public_schema["league.match.update"]

        await match.update(**paramters)

        return response((await match.scoreboard()).api_schema(public_schema))

    @requires("league.match.end")
    @required_states("match")
    async def delete(self, request: Request) -> JSONResponse:
        """Used to end a match, uploads demo too.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        match = request.state.match
        public_schema = request.state.public_schema["league.match.end"]

        return response((await match.end()).api_schema(public_schema))


class LeagueMatchScoreboardAPI(HTTPEndpoint):
    @requires("league.match.scoreboard")
    @required_states("match")
    async def get(self, request: Request) -> JSONResponse:
        """Used to get match scoreboard.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        match = request.state.match
        public_schema = request.state.public_schema["league.match.scoreboard"]

        cache = CacheScoreboard(match.upper.league_id, match.match_id)

        cache_get = await cache.get()
        if cache_get:
            return response(cache_get)

        return response((await match.scoreboard()).api_schema(public_schema))
