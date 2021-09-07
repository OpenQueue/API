# -*- coding: utf-8 -*-

import re

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from urllib.parse import urlencode

from ....resources import Config, Sessions


class SteamAuth(HTTPEndpoint):
    """Handles steam auth
       Creates user when logged in.
    """

    async def get(self, request: Request) -> RedirectResponse:
        if "login" not in request.session:
            return RedirectResponse("/login")

        params = request.query_params
        if ("openid.ns" in params and "openid.mode" in params
            and "openid.claimed_id" in params and "openid.assoc_handle"
            and "openid.signed" in params and "openid.sig" in params
            and "openid.op_endpoint" in params and "openid.identity" in params
            and "openid.return_to" in params
                and "openid.response_nonce" in params):

            validation = {
                "openid.assoc_handle": params["openid.assoc_handle"],
                "openid.signed": params["openid.signed"],
                "openid.sig": params["openid.sig"],
                "openid.ns": params["openid.ns"],
            }

            signed = params["openid.signed"].split(",")
            for item in signed:
                item_arg = "openid." + item

                if item_arg in params and params[item_arg] not in validation:
                    validation[item_arg] = params[item_arg]

            validation["openid.mode"] = "check_authentication"

            resp = await Sessions.requests.post(
                "https://steamcommunity.com/openid/login", data=validation
            )
            if resp.status == 200:
                data = await resp.text()

                if "is_valid:true" in data:
                    matched = re.search(
                        "https://steamcommunity.com/openid/id/(\\d+)",
                        params["openid.claimed_id"]
                    )

                    if matched and matched.group(1):
                        steam_id = matched.group(1)

                        await Sessions.base.user(
                            request.session["login"]["identifiers"]["user"]
                        ).update(
                            steam_id=steam_id
                        )

                        request.session["login"]["identifiers"][
                            "steam"
                        ] = steam_id
            else:
                # Send server log that steam login errorred!
                pass
        else:
            params = {
                "openid.ns": "http://specs.openid.net/auth/2.0",
                "openid.identity":
                "http://specs.openid.net/auth/2.0/identifier_select",
                "openid.claimed_id":
                "http://specs.openid.net/auth/2.0/identifier_select",
                "openid.mode": "checkid_setup",
                "openid.return_to": "{}auth/site/steam/".format(
                    Config.backend_url
                ),
                "openid.realm": Config.backend_url,
            }

            return RedirectResponse(
                "https://steamcommunity.com/openid/login?" + urlencode(params)
            )

        return RedirectResponse("/register")
