# -*- coding: utf-8 -*-

from starlette.routing import Route, Mount

from webargs_starlette import WebargsHTTPException
from starlette.exceptions import HTTPException
from OpenQueue.exceptions import OpenQueueException, UsersBanned


# Metrics
from starlette_prometheus import metrics


# -----------------------
# Version 1 API Endpoints
# -----------------------

# User Endpoints
from .api.v1.user import UserAPI

# League Endpoints
from .api.v1.league.user import (
    LeagueUserAPI,
    LeagueUserBanAPI,
    LeagueUserMatchesAPI
)
from .api.v1.league.users import LeagueUsersAPI
from .api.v1.league.match import (
    LeagueMatchCreateAPI,
    LeagueMatchAPI,
    LeagueMatchScoreboardAPI
)
from .api.v1.league.matches import LeagueMatchesAPI

# Integrations
from .api.v1.integrations import IntegrationsAPI
from .api.v1.league.integrations import LeagueIntegrationsAPI

# Caching Route
from .caching import CachingRoute

# Error handlers
from .errors import (
    error,
    payload_error,
    server_error
)

# --------------
# Auth Endpoints
# --------------
from .auth.site.login import (
    LogoutAuth,
    LoginSession,
    LoginCreate,
    LoginAuth
)
from .auth.site.steam import SteamAuth
from .auth.site.discord import DiscordAuth
from .auth.site.scopes import MyScopes
from .auth.site.confirmation import EmailConfirmation
from .auth.login import GenerateLoginToken, UserToken, LoginRedirect


ERROR_HANDLERS = {
    UsersBanned: error,
    OpenQueueException: error,
    WebargsHTTPException: payload_error,
    HTTPException: server_error
}


ROUTES = [
    Mount("/api", routes=[
        Mount("/v1", routes=[
            Route("/user/", UserAPI),
            Route("/integrations/", IntegrationsAPI),
            # Any league routes are accessible via the public api.
            Mount("/league", routes=[
                Route("/integrations/", LeagueIntegrationsAPI),
                Mount("/user", routes=[
                    Route("/", LeagueUserAPI),
                    Route("/ban/", LeagueUserBanAPI),
                    Route("/matches/", LeagueUserMatchesAPI)
                ]),
                Mount("/users", routes=[
                    Route("/", LeagueUsersAPI)
                ]),
                Mount("/match", routes=[
                    Route(
                        "/{map_selection}/{player_selection}/{captain_selection}/",  # noqa: E501
                        LeagueMatchCreateAPI
                    ),
                    Route("/scoreboard/", LeagueMatchScoreboardAPI),
                    Route("/", LeagueMatchAPI)
                ]),
                Mount("/matches", routes=[
                    Route("/", LeagueMatchesAPI)
                ])
            ]),
        ]),
        Mount("/auth", routes=[
            # /auth/site routes are for skrim.gg login related stuff
            Mount("/site", routes=[
                Route("/login/", LoginAuth, name="LoginAuth"),
                Route("/logout/", LogoutAuth),
                Route("/create/", LoginCreate),
                Route("/session/", LoginSession),
                Route("/discord/", DiscordAuth),
                Route("/steam/", SteamAuth),
                Route("/scopes/", MyScopes),
                Route("/confirmation/{email_code}/", EmailConfirmation)
            ]),
            Route("/generate/", GenerateLoginToken),
            Route("/login/", LoginRedirect),
            Route("/user/", UserToken),
        ]),
        Route("/caching/", CachingRoute),
        Route("/metrics/", metrics),
    ]),
]
