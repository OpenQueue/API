from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.authentication import requires

from ....resources import Sessions


class EmailConfirmation(HTTPEndpoint):
    @requires("site")
    async def get(self, request: Request) -> RedirectResponse:
        if "login" in request.session:
            user = Sessions.base.user(
                request.session["login"]["identifiers"]["user"]
            )
            if await user.validate_email_code(
                    request.path_params["email_code"]):
                await user.update(email_confirmed=True)

                request.session["login"]["email_confirmed"] = True

                return RedirectResponse("/register")

        return RedirectResponse("/code-invalid")
