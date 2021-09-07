"""Handles Skrim.gg open login system.
"""

from secrets import token_urlsafe
from typing import Dict, Tuple
from datetime import datetime

from .exceptions import InvalidToken


class LoginTokens:
    login_tokens: Dict[str, str] = {}
    user_tokens: Dict[str, Tuple[datetime, str]] = {}

    def generate_login_token(self, league_id: str) -> str:
        """Used to generate a login token

        Parameters
        ----------
        league_id : str

        Returns
        -------
        str
            Login token
        """

        login_token = token_urlsafe(36)
        self.login_tokens[login_token] = league_id
        return login_token

    def generate_user_token(self, league_id: str, login_token: str,
                            user_id: str) -> str:
        """Used to generate a user login token

        Parameters
        ----------
        league_id : str
        login_token : str
        user_id : str

        Returns
        -------
        str
            User login token

        Raises
        ------
        InvalidToken
        """

        if (login_token in self.login_tokens and
                self.login_tokens[login_token] == league_id):
            self.login_tokens.pop(login_token)

            user_login_token = token_urlsafe(36)
            self.user_tokens[user_login_token] = (datetime.now(), user_id)

            return user_login_token
        else:
            raise InvalidToken()

    def get_user_id(self, user_login_token: str) -> str:
        """Used to get a user id from a user login token

        Parameters
        ----------
        user_login_token : str

        Returns
        -------
        str
            User ID
        """

        if user_login_token in self.user_tokens:
            seconds = (
                datetime.now() - self.user_tokens[user_login_token][0]
            ).seconds
            if seconds > 45:
                self.user_tokens.pop(user_login_token)
                raise InvalidToken()
            else:
                user_id = self.user_tokens[user_login_token]
                self.user_tokens.pop(user_login_token)
                return user_id[1]
        else:
            raise InvalidToken()
