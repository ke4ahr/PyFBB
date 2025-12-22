# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Legacy setup.py for PyFBB compatibility.

Note: Modern Python packaging prefers pyproject.toml (already present).
This setup.py is provided for backward compatibility with older tools
that require it (e.g., some editable installs or legacy workflows).

It simply delegates to the build system defined in pyproject.toml.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()
