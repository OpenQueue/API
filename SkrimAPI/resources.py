# -*- coding: utf-8 -*-

from typing import Dict
import aiohttp
import proxycheck

from OpenQueue import OpenQueue
from OpenQueue.queue import Queue
from OpenQueue.settings.upload import B2Settings, PfpSettings
from OpenQueue.settings.webhook import WebhookSettings

from databases import Database
from aiocache import Cache
from aioauth_client import DiscordClient

from .settings.discord import DiscordSettings
from .settings.proxy_check import ProxyCheckSettings
from .settings.api import ApiSettings

from .login import LoginTokens


class Sessions:
    base: OpenQueue
    database: Database
    requests: aiohttp.ClientSession
    cache: Cache
    discord_auth: DiscordClient
    proxy: proxycheck.Awaiting
    login_token: LoginTokens


class Config:
    backend_url: str
    frontend_url: str
    discord: DiscordSettings
    proxy: ProxyCheckSettings
    api: ApiSettings
    b2: B2Settings
    pfp: PfpSettings
    webhooks: WebhookSettings


class Queues:
    active: Dict[str, Queue] = {}
