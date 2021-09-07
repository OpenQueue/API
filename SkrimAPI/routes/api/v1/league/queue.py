# -*- coding: utf-8 -*-

from starlette.endpoints import HTTPEndpoint
from starlette.authentication import requires
from starlette.requests import Request
from starlette.responses import JSONResponse

from webargs import fields
from webargs_starlette import use_args

from ....response import response
from ....decorators import required_states

from .....resources import Sessions


class QueueAPI(HTTPEndpoint):
    @requires("queue.get")
    @required_states("queue")
    async def get(self, request: Request) -> JSONResponse:
        """Used to get a queue.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        queue = request.state.queue
        public_schema = request.state.public_schema["queue.get"]

        return response((queue.get()).api_schema(public_schema))

    @use_args({"capacity": fields.Integer()})
    @requires("create_queue")
    async def post(self, request: Request, paramters: dict) -> JSONResponse:
        """Used to create a queue.

        Parameters
        ----------
        request : Request
        paramters : dict

        Returns
        -------
        response
        """

        public_schema = request.state.public_schema["create_queue"]

        queue = Sessions.base.create_queue(**paramters)
        queue.active[queue.queue_id] = queue

        return response((
            queue.get()
        ).api_schema(public_schema))

    @requires("queue.user.join")
    @required_states(["queue", "user"])
    async def put(self, request: Request) -> JSONResponse:
        """Used to put a user into queue.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        queue = request.state.queue
        public_schema = request.state.public_schema["queue.user.join"]

        await queue.join(request.state.user)

        return response((
            queue.get()
        ).api_schema(public_schema))

    @requires("queue.user.leave")
    @required_states(["queue", "user"])
    async def patch(self, request: Request) -> JSONResponse:
        """Used to make user leave queue.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        queue = request.state.queue
        public_schema = request.state.public_schema["queue.user.leave"]

        queue.leave(request.state.user)

        return response((
            queue.get()
        ).api_schema(public_schema))

    @requires("queue.end")
    @required_states("queue")
    async def delete(self, request: Request) -> JSONResponse:
        """Used to end queue.

        Parameters
        ----------
        request : Request

        Returns
        -------
        response
        """

        queue = request.state.queue
        queue.active.pop(queue.queue_id, None)
        return response()
