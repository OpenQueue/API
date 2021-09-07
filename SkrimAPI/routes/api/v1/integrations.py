from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.responses import JSONResponse

from ...response import response

from ....misc import SkrimRequest
from ....resources import Sessions


class IntegrationsAPI(HTTPEndpoint):
    @requires("site")
    async def get(self, request: SkrimRequest) -> JSONResponse:
        return response([
            integration.api_schema() async for integration
            in Sessions.base.integrations()
        ])
