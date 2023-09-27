# coding: utf-8

"""
    SnapTrade

    Connect brokerage accounts to your app for live positions and trading

    The version of the OpenAPI document: 1.0.0
    Contact: api@snaptrade.com
    Created by: https://snaptrade.com/
"""

from datetime import datetime, date
import typing
from enum import Enum
from typing_extensions import TypedDict, Literal

from snaptrade_client.type.currency import Currency
from snaptrade_client.type.exchange import Exchange
from snaptrade_client.type.security_type import SecurityType

class RequiredUniversalSymbol(TypedDict):
    pass

class OptionalUniversalSymbol(TypedDict, total=False):
    id: str

    symbol: str

    raw_symbol: str

    description: typing.Optional[str]

    currency: Currency

    exchange: Exchange

    type: SecurityType

    currencies: typing.List[Currency]

class UniversalSymbol(RequiredUniversalSymbol, OptionalUniversalSymbol):
    pass
