# -*- coding: utf-8 -*-

"""
Importable constants value.
"""

from .vendor.better_enum import BetterStrEnum


class TokenTypeEnum(BetterStrEnum):
    raw = "Token::Raw"
    jmespath = "Token::Jmespath"
    sub = "Token::Sub"
    join = "Token::Join"
    map = "Token::Map"

TYPE = "type"
