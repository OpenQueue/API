# -*- coding: utf-8 -*-

import logging
import proxycheck

from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware

from starlette_prometheus import PrometheusMiddleware

from aiocache import Cache
from aioauth_client import DiscordClient
from secrets import token_urlsafe

from OpenQueue import OpenQueue
from OpenQueue.resources import Sessions as BaseSessions
from OpenQueue.resources import Config as BaseConfig
from OpenQueue.key_loader import KeyLoader

from .routes import ROUTES, ERROR_HANDLERS
from .middleware import AuthenticateMiddleware

from .resources import Sessions, Config

from .settings.discord import DiscordSettings
from .settings.proxy_check import ProxyCheckSettings
from .settings.api import ApiSettings

from .login import LoginTokens


__version__ = "0.0.1"
__url__ = "https://github.com/SkrimGG"
__description__ = "API for Skrim."
__author__ = "WardPearce"
__author_email__ = "wardpearce@protonmail.com"
__license__ = "Copyright WardPearce 2020 - 2021"


logger = logging.getLogger("SkrimAPI")


class SkrimAPI(Starlette):
    def __init__(self, skrim: OpenQueue,
                 discord_settings: DiscordSettings,
                 proxy_check_settings: ProxyCheckSettings,
                 api_settings: ApiSettings,
                 backend_url: str,
                 frontend_url: str,  **kwargs) -> None:
        """Nexus League's API.

        Parameters
        ----------
        skrim : OpenQueue
        discord_settings : DiscordSettings
        region_settings : RegionSettings
        api_settings : ApiSettings
        proxy_check_settings : ProxyCheckSettings
        backend_url : str
        frontend_url : str
        """

        assert isinstance(skrim, OpenQueue)
        assert isinstance(discord_settings, DiscordSettings)
        assert isinstance(proxy_check_settings, ProxyCheckSettings)
        assert isinstance(api_settings, ApiSettings)
        assert isinstance(backend_url, str)
        assert isinstance(frontend_url, str)

        Sessions.base = skrim

        Config.proxy = proxy_check_settings
        Config.discord = discord_settings
        Config.backend_url = (
            backend_url if backend_url[-1:] == "/" else backend_url + "/"
        )
        Config.frontend_url = (
            frontend_url if frontend_url[-1:] == "/" else frontend_url + "/"
        )
        Config.api = api_settings
        Config.b2 = BaseConfig.b2
        Config.pfp = BaseConfig.pfp
        Config.webhooks = BaseConfig.webhooks

        session_key = KeyLoader("session").load()
        if not session_key:
            session_key = KeyLoader("session").save(token_urlsafe(24))

        middlewares = [
            Middleware(
                SessionMiddleware,
                secret_key=session_key
            ),
            Middleware(
                AuthenticationMiddleware,
                backend=AuthenticateMiddleware()
            ),
            Middleware(CORSMiddleware, allow_origins=["*"]),
            Middleware(ProxyHeadersMiddleware, trusted_hosts="*"),
            Middleware(PrometheusMiddleware)
        ]

        if "middleware" in kwargs:
            kwargs["middleware"] += middlewares
        else:
            kwargs["middleware"] = middlewares

        if "routes" in kwargs:
            kwargs["routes"] += ROUTES
        else:
            kwargs["routes"] = ROUTES

        if "exception_handlers" in kwargs:
            kwargs["exception_handlers"] += ERROR_HANDLERS
        else:
            kwargs["exception_handlers"] = ERROR_HANDLERS

        if "on_startup" in kwargs:
            kwargs["on_startup"].append(self.startup)
        else:
            kwargs["on_startup"] = [self.startup]

        if "on_shutdown" in kwargs:
            kwargs["on_shutdown"].append(self.shutdown)
        else:
            kwargs["on_shutdown"] = [self.shutdown]

        super().__init__(**kwargs)

    async def startup(self) -> None:
        """Called before server setup.
        """

        try:
            Sessions.cache = Cache(Cache.REDIS)
            await Sessions.cache.exists("connection")
        except ConnectionRefusedError:
            Sessions.cache = Cache(Cache.MEMORY)
            logger.warning(
                "Memory cache being used, use redis for production."
            )

        await Sessions.base.startup()

        Sessions.requests = BaseSessions.requests
        Sessions.database = BaseSessions.database

        Sessions.proxy = proxycheck.Awaiting(
            Config.proxy.key
        )

        Sessions.login_token = LoginTokens()

        Sessions.discord_auth = DiscordClient(
            Config.discord.client_id,
            Config.discord.client_secret
        )

    async def shutdown(self) -> None:
        """Called after server shutdown.
        """

        await Sessions.cache.close()
        await Sessions.base.shutdown()
        await Sessions.proxy.close()
