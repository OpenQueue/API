# -*- coding: utf-8 -*-

from typing import Tuple, Union
from sqlalchemy.sql import select
from proxycheck.exceptions import ProxyCheckException

from .resources import Sessions
from .tables import proxy_table


class ProxyCheck:
    def __init__(self, ip: str, discord_id: int) -> None:
        """Used to use proxy check cached.

        Parameters
        ----------
        ip : str
        discord_id : imt
        """

        self.ip = Sessions.proxy.ip(ip)
        self.discord_id = discord_id

    async def get(self) -> Tuple[bool, str, Union[int, None]]:
        """Used to get IP details

        Returns
        -------
        bool
            If vpn.
        str
            ISO code.
        int
            Discord ID of user if IP already regerseted
            will ne None if IP only just cached.
        """

        row = await Sessions.database.fetch_one(
            select([
                proxy_table.c.proxy,
                proxy_table.c.isocode,
                proxy_table.c.discord_id
            ]).select_from(proxy_table).where(
                proxy_table.c.ip == self.ip.ip
            )
        )

        if row:
            return row["proxy"], row["isocode"], None

        try:
            details = await self.ip.get(asn=True, vpn=True)
        except ProxyCheckException:
            return False, "Unknown", self.discord_id
        else:
            details.isocode = details.isocode.upper()

            await Sessions.database.execute(
                proxy_table.insert().values(
                    ip=self.ip.ip,
                    proxy=details.proxy,
                    isocode=details.isocode,
                    discord_id=self.discord_id
                )
            )

            return details.proxy, details.isocode, self.discord_id
