from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.authentication import requires

from marshmallow import validate
from webargs import fields
from webargs_starlette import use_args

from ....resources import Sessions
from ...response import error_response, response


class LogoutAuth(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        request.session.pop("login", None)
        return Response()


class LoginSession(HTTPEndpoint):
    @requires("site")
    async def get(self, request: Request) -> JSONResponse:
        if "login" in request.session:
            return response(request.session["login"])
        else:
            return error_response()


class LoginCreate(HTTPEndpoint):
    @use_args({
        "email": fields.Email(required=True, validates=validate.Range(3, 255)),
        "password": fields.Str(
            required=True, validates=validate.Range(8, 128)
        ),
        "name": fields.Str(required=True, validates=validate.Range(3, 16))
    })
    @requires("site")
    async def post(self, request: Request, params: dict
                   ) -> JSONResponse:
        if "login" in request.session:
            return error_response("Already logged in")

        model, _ = await Sessions.base.create_user(
            email=params["email"],
            password=params["password"],
            name=params["name"]
        )

        data = model.api_schema(False)
        request.session["login"] = data

        return response(data)


class LoginAuth(HTTPEndpoint):
    @use_args({
        "email": fields.Email(required=True, validates=validate.Range(8, 255)),
        "password": fields.Str(
            required=True, validates=validate.Range(8, 128)
        )
    })
    @requires("site")
    async def post(self, request: Request, params: dict
                   ) -> JSONResponse:
        if "login" in request.session:
            return error_response("Already logged in")

        model, _ = await Sessions.base.login(
            email=params["email"],
            password=params["password"]
        ).check()

        data = model.api_schema(False)
        request.session["login"] = data

        return response(data)
