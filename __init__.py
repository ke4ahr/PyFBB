# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
PyFBB - Pure Python F6FBB packet radio BBS forwarding library
"""

from .fbb.forwarder import FBBForwarder, FBBProtocolError
from .fbb.lzhuf import LZHUF_Comp
from .fbb.transport import (
    KISSTransport,
    AX25Connection,
    AGWTransport,
    TCPTransport
)

__version__ = "0.1.2"
__author__ = "Kris Kirby, KE4AHR"

__all__ = [
    "FBBForwarder",
    "FBBProtocolError",
    "LZHUF_Comp",
    "KISSTransport",
    "AX25Connection",
    "AGWTransport",
    "TCPTransport",
]
