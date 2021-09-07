# -*- coding: utf-8 -*-

from typing import Any
from starlette.responses import JSONResponse


def response(data: Any = {}, *args, **kwargs) -> JSONResponse:
    return JSONResponse({"data": data, "error": None}, *args, **kwargs)


def error_response(error: Any = {}, *args, **kwargs) -> JSONResponse:
    return JSONResponse({"data": None, "error": error}, *args, **kwargs)
