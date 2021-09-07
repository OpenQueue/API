from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ....resources import Config, Sessions


class DiscordAuth(HTTPEndpoint):
    """Handles auth flow for Nexus League
       Redirects to SteamAuth if steam account not linked.
    """

    async def get(self, request: Request) -> RedirectResponse:
        if "login" not in request.session:
            return RedirectResponse("/login")

        redirect_uri = Config.backend_url + "auth/site/discord/"

        if "code" not in request.query_params:
            return RedirectResponse(
                Sessions.discord_auth.get_authorize_url(
                    scope="guilds.join identify email",
                    prompt="consent",
                    redirect_uri=redirect_uri
                )
            )

        # Required for .user_info() to work...
        await Sessions.discord_auth.get_access_token(
            request.query_params["code"],
            redirect_uri=redirect_uri
        )

        _, data = await Sessions.discord_auth.user_info()

        request.session["login"]["identifiers"]["discord"] = data["id"]
        await Sessions.base.user(
            request.session["login"]["identifiers"]["user"]
        ).update(
            discord_id=data["id"]
        )

        return RedirectResponse("/register")
