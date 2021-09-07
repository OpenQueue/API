# -*- coding: utf-8 -*-


class DiscordSettings:
    def __init__(self, client_id: str, client_secret: str, bot_token: str,
                 route: str = "https://discord.com/api/") -> None:
        """Discord settings

        Parameters
        ----------
        client_id : str
        client_secret : str
        bot_token : str
        route : str, optional
            by default "https://discord.com/api/"
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.bot_token = "Bot " + bot_token
        self.route = route if route[-1:] == "/" else route + "/"
