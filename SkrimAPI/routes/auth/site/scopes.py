from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.authentication import requires

from ...response import response


class MyScopes(HTTPEndpoint):
    @requires("site.loggedIn")
    async def get(self, request: Request) -> JSONResponse:
        return response(list(
            request.state.public_schema.keys()
        ))
