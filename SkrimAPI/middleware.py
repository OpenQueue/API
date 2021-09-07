# -*- coding: utf-8 -*-

import binascii
import bcrypt

from typing import Tuple, Union
from base64 import b64decode

from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
    AuthCredentials
)
from starlette.responses import JSONResponse
from starlette.requests import Request

from .authentication import api_key, admin_scopes
from .resources import Config, Queues, Sessions
from .caching import CacheAPIKey


class AuthenticateMiddleware(AuthenticationBackend):
    async def authenticate(self, request: Request
                           ) -> Union[
                               Tuple[AuthCredentials, SimpleUser],
                               None, JSONResponse]:
        """Used to authenticate, scope & state requests.
        """

        if "Authorization" in request.headers:
            auth = request.headers["Authorization"]
            try:
                scheme, credentials = auth.split()
                if scheme.lower() != "basic":
                    return
                decoded = b64decode(credentials).decode("ascii")
            except (ValueError, UnicodeDecodeError, binascii.Error):
                raise AuthenticationError()

            _, _, password = decoded.partition(":")

            # If CachingWebhook in headers, check its password.
            if "CachingWebhook" in request.headers:
                hashed_password = bcrypt.hashpw(
                    Config.webhooks.key.encode(),
                    bcrypt.gensalt()
                )
                if bcrypt.checkpw(password.encode(), hashed_password):
                    return AuthCredentials(["caching"]), SimpleUser("root")

            cache = CacheAPIKey(password)
            cache_get = await cache.get()
            if cache_get:
                request.state.league, user_id, scopes = cache_get
            else:
                try:
                    (
                        request.state.league,
                        user_id,
                        scopes
                    ) = await api_key(password)
                except AuthenticationError:
                    raise
                else:
                    await cache.set((
                        request.state.league,
                        user_id,
                        scopes
                    ))

            if "user" in request.query_params:
                request.state.user = request.state.league.user(
                    request.query_params["user"]
                )

                if "ban" in request.query_params:
                    request.state.ban = request.state.user.ban(
                        request.query_params["ban"]
                    )

            if "match" in request.query_params:
                request.state.match = request.state.league.match(
                    request.query_params["match"]
                )

            if "queue" in request.query_params:
                if request.query_params["queue"] in Queues.active:
                    request.state.queue = Queues.active[
                        request.query_params["queue"]
                    ]

            request.state.public_schema = scopes
            return AuthCredentials(list(scopes.keys())), SimpleUser(user_id)

        elif ("login" in request.session and
                request.session["login"]["email_confirmed"]):
            user_id = request.session["login"]["identifiers"]["user"]
            scopes = ["site", "site.loggedIn"]
            request.state.public_schema = {}

            if user_id in Config.api.root_users:
                scopes.append("site.rootLoggedIn")

            if ("user" in request.query_params and
                    "league" not in request.query_params):
                scopes.append("user")

                request.state.user = Sessions.base.user(
                    request.query_params["user"]
                )

                if request.query_params["user"] == user_id:
                    scopes.append("user.owner")
                    request.state.public_schema["user.owner"] = False
                    request.state.public_schema["user"] = False
                else:
                    request.state.public_schema["user"] = True

                if "queue" in request.query_params:
                    if request.query_params["queue"] in Queues.active:
                        request.state.queue = Queues.active[
                            request.query_params["queue"]
                        ]

                        scopes += [
                            "queue.user.join", "queue.user.leave", "queue.get"
                        ]

                        request.state.public_schema["queue.get"] = True
                        request.state.public_schema["queue.user.join"] = True
                        request.state.public_schema["queue.user.leave"] = True
            elif "league" in request.query_params:
                scopes += ["league", "league.matches", "league.users"]

                request.state.public_schema["league.matches"] = True

                request.state.league = Sessions.base.league(
                    request.query_params["league"]
                )

                if (request.query_params["league"] in
                        request.session["login"]["league_ids"]):
                    scopes.append("league.owner")

                    request.state.public_schema["league"] = False
                    request.state.public_schema["league.owner"] = False
                else:
                    request.state.public_schema["league"] = True

                if (
                    "check_admin" in request.query_params
                    and request.query_params["check_admin"].lower() == "true"
                   ):
                    allowed_scopes = await admin_scopes(
                        user_id,
                        request.query_params["league"]
                    )

                    request.state.public_schema = {
                        **request.state.public_schema,
                        **allowed_scopes
                    }

                    scopes += list(allowed_scopes.keys())

                if "user" in request.query_params:
                    scopes += ["league.user", "league.user.matches"]

                    request.state.public_schema["league.user.matches"] = True

                    if request.query_params["user"] == user_id:
                        scopes.append("league.user.owner")
                        request.state.public_schema["league.user"] = False
                        request.state.public_schema[
                            "league.user.owner"
                        ] = False
                    else:
                        request.state.public_schema["league.user"] = True

                    request.state.user = request.state.league.user(
                        request.query_params["user"]
                    )

                    if "ban" in request.query_params:
                        scopes.append("league.user.ban")
                        request.state.public_schema["league.user.ban"] = True

                        request.state.ban = request.state.user.ban(
                            request.query_params["ban"]
                        )

                if "match" in request.query_params:
                    scopes += ["league.match", "league.match.scoreboard"]

                    request.state.public_schema["league.match"] = True
                    request.state.public_schema[
                        "league.match.scoreboard"
                    ] = True

                    request.state.match = request.state.league.match(
                        request.query_params["match"]
                    )

            return AuthCredentials(scopes), SimpleUser(user_id)
        else:
            return AuthCredentials(["site"]), SimpleUser("")
