from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import JSONResponse

from ....response import response
from ....decorators import required_states

from .....misc import SkrimRequest


class LeagueIntegrationsAPI(HTTPEndpoint):
    @requires("site")
    @required_states("league")
    async def get(self, request: SkrimRequest) -> JSONResponse:
        return response([
            integration.api_schema() async for integration
            in request.state.league.integrations()
        ])
