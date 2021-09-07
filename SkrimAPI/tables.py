# -*- coding: utf-8 -*-

from sqlalchemy import (
    String,
    Boolean,
    Table,
    Column,
    TIMESTAMP,
    ForeignKey,
    PrimaryKeyConstraint,
    Integer,
    BigInteger
)
from datetime import datetime
from OpenQueue.tables import metadata


proxy_table = Table(
    "proxy_table",
    metadata,
    Column(
        "ip",
        String(length=39),
        primary_key=True
    ),
    Column(
        "proxy",
        Boolean
    ),
    Column(
        "isocode",
        String(length=3)
    ),
    Column(
        "discord_id",
        BigInteger
    )
)


# API Scopes table
scopes_table = Table(
    "scopes",
    metadata,
    Column(
        "scope_id",
        Integer,
        primary_key=True
    ),
    Column(
        "scope",
        String(length=30)
    ),
    Column(
        "description",
        String(length=255)
    ),
    Column(
        "root_only",
        Boolean
    )
)


# API Key table
api_key_table = Table(
    "api_key",
    metadata,
    Column(
        "api_key",
        String(length=32),
        primary_key=True
    ),
    Column(
        "user_id",
        String(length=36),
        ForeignKey("user.user_id")
    ),
    Column(
        "timestamp",
        TIMESTAMP,
        default=datetime.now
    ),
    Column(
        "league_id",
        String(length=6),
        ForeignKey("league.league_id")
    ),
    mysql_engine="InnoDB",
    mysql_charset="utf8mb4"
)


# Key scopes
key_scopes_table = Table(
    "key_scopes",
    metadata,
    Column(
        "api_key",
        String(length=32),
        ForeignKey("api_key.api_key"),
        primary_key=True
    ),
    Column(
        "scope_id",
        Integer,
        ForeignKey("scopes.scope_id"),
        primary_key=True
    ),
    Column(
        "public_schema",
        Boolean,
        default=True
    ),
    PrimaryKeyConstraint(
        "api_key",
        "scope_id"
    )
)


# Admin scopes
admin_scopes_table = Table(
    "admin_scopes",
    metadata,
    Column(
        "user_id",
        String(length=36),
        ForeignKey("admin.user_id"),
        primary_key=True
    ),
    Column(
        "league_id",
        String(length=6),
        ForeignKey("admin.league_id"),
        primary_key=True
    ),
    Column(
        "scope_id",
        Integer,
        ForeignKey("scopes.scope_id"),
        primary_key=True
    ),
    Column(
        "public_schema",
        Boolean,
        default=True
    ),
    PrimaryKeyConstraint(
        "user_id",
        "league_id",
        "scope_id"
    )
)
