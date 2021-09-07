from typing import Union
from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import (
    JSONResponse,
    RedirectResponse,
    PlainTextResponse
)

from ...resources import Sessions
from ...misc import SkrimRequest

from ..response import error_response, response
from ..decorators import required_states


class GenerateLoginToken(HTTPEndpoint):
    @requires("league.login.generate")
    @required_states("league")
    async def post(self, request: SkrimRequest) -> JSONResponse:
        return response({
            "token": Sessions.login_token.generate_login_token(
                request.state.league.league_id
            )
        })


class UserToken(HTTPEndpoint):
    @requires("league.login.user.get")
    async def get(self, request: SkrimRequest) -> JSONResponse:
        if "user_token" in request.query_params:
            return response({
                "user": Sessions.login_token.get_user_id(
                    request.query_params["user_token"]
                )
            })
        else:
            return error_response("user_token not given", status_code=400)


class LoginRedirect(HTTPEndpoint):
    async def get(self, request: SkrimRequest
                  ) -> Union[RedirectResponse, PlainTextResponse]:
        if "redirect" not in request.query_params:
            return PlainTextResponse("No redirect")

        if "login_token" not in request.query_params:
            return PlainTextResponse("No login token")

        if "league_id" not in request.query_params:
            return PlainTextResponse("No league id")

        if ("login" in request.session and
            "user_id" in request.query_params and
            request.query_params["user_id"] ==
                request.session["login"]["identifiers"]["user"]):
            return RedirectResponse(
                "{}?user_token={}".format(
                    request.query_params["redirect"],
                    Sessions.login_token.generate_user_token(
                        request.query_params["league_id"],
                        request.query_params["login_token"],
                        request.session["login"]["identifiers"]["user"]
                    )
                )
            )
        else:
            return RedirectResponse(
                "/login?login_token={}&league_id={}&redirect={}".format(
                    request.query_params["login_token"],
                    request.query_params["league_id"],
                    request.query_params["redirect"]
                )
            )
