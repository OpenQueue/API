# -*- coding: utf-8 -*-


class ProxyCheckSettings:
    def __init__(self, dev_mode: bool,
                 key: str = None, allow_vpns: bool = False,
                 allow_alts: bool = False) -> None:
        """Configure proxy check.

        Parameters
        ----------
        dev_mode : bool
        key : str, optional
            by default None
        allow_vpns : bool, optional
            by default False
        allow_alts : bool, optional
            by default False
        """

        self.dev_mode = dev_mode
        self.key = key
        self.allow_vpns = allow_vpns
        self.allow_alts = allow_alts
