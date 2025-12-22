# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
PyFBB - Pure Python implementation of the F6FBB packet radio BBS forwarding protocol.

Key Features:
    - Supports both ASCII and binary (compressed) forwarding modes
    - Authentic LZHUF compression (original FBB algorithm)
    - Full reverse forwarding support via the `FR` command
    - Clean, modern, well-documented API
    - Comprehensive unit and integration tests

Quick Import Example:
    >>> from pyfbb import FBBForwarder, FBBProtocolError, LZHUF_Comp
"""

from .fbb.forwarder import FBBForwarder, FBBProtocolError
from .fbb.lzhuf import LZHUF_Comp

__version__ = "0.1.0"
__author__ = "Kris Kirby, KE4AHR"
__license__ = "LGPL-3.0-or-later"
__description__ = "Pure Python F6FBB packet radio BBS forwarding protocol implementation"

__all__ = [
    "FBBForwarder",
    "FBBProtocolError",
    "LZHUF_Comp",
]
