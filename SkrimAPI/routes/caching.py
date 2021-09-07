from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import Response

from OpenQueue.models.match import MatchModel

from ..caching import (
    CacheMatches,
    CacheScoreboard,
    CacheMatch
)


class CachingRoute(HTTPEndpoint):
    @requires("caching")
    async def post(self, request: Request) -> Response:
        payload = await request.json()
        if "__wh_event_id" not in payload:
            return Response(status_code=400)

        event_id = payload["__wh_event_id"]
        payload.pop("__wh_event_id")

        # League match caching
        if event_id in (141201, 141202, 141203):
            match_id = payload["match_id"]
            league_id = payload["league_id"]

            await CacheScoreboard(league_id, match_id).set(payload)

            match_data = MatchModel(**payload).api_schema()
            await CacheMatch(league_id, match_id).set(match_data)

            matches_cache = CacheMatches(payload["league_id"])

            current_matches: list = await matches_cache.get()
            if current_matches:
                current_matches.insert(0, match_data)

                await matches_cache.set(current_matches)
            else:
                await matches_cache.set([match_data])

        # League caching
        elif event_id in (141207, 141208):
            pass
        # League user caching
        elif event_id in (141211, 141212):
            pass

        return Response()
