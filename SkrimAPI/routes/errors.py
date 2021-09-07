# -*- coding: utf-8 -*-

from typing import Union
from starlette.requests import Request
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from webargs_starlette import WebargsHTTPException
from OpenQueue.exceptions import OpenQueueException

from .response import error_response

from ..exceptions import SkrimAPIException


def error(request: Request, exc: Union[OpenQueueException, SkrimAPIException]
          ) -> JSONResponse:
    return error_response(
        error=exc.msg,
        status_code=exc.status_code
    )


def server_error(request: Request, exc: HTTPException) -> JSONResponse:
    return error_response(
        error=exc.detail,
        status_code=exc.status_code
    )


def payload_error(request: Request, exc: WebargsHTTPException
                  ) -> JSONResponse:
    return error_response(
        error=exc.messages,
        status_code=exc.status_code,
        headers=exc.headers
    )
