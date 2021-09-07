# -*- coding: utf-8 -*-

from starlette.requests import Request
from starlette.datastructures import State

from OpenQueue import League, User, Queue


class SkrimState(State):
    league: League
    user: User
    queue: Queue


class SkrimRequest(Request):
    state: SkrimState
