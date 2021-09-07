# -*- coding: utf-8 -*-

from functools import wraps
from typing import List, Callable, Union

from .response import error_response


def required_states(states: Union[str, List[str]]) -> Callable:
    """Used to set request states required.

    Parameters
    ----------
    states : Union[str, List[str]]

    Notes
    -----
    When using only check for states you're using,
    if a request new states later on. Add them when needed.
    """

    states = [states] if isinstance(states, str) else list(states)

    def decorator(func) -> Callable:
        @wraps(func)
        async def _validate(*args, **kwargs) -> func:
            for state in states:
                if not hasattr(args[1].state, state):
                    return error_response(
                        "Required state '{}' not given".format(state),
                        status_code=400
                    )

            return await func(*args, **kwargs)

        return _validate

    return decorator
