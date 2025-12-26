-----
README.md
-----

    # PyFBB

    **PyFBB** is a pure-Python library implementing the classic **F6FBB** packet radio BBS forwarding protocol with full AX.25 integration.

    ## Features
    - Full FBB protocol (ASCII, binary, B2F) with resume, XFWD, traffic limiting
    - Full Winlink B2F compatibility (gzip option, large attachments, RMS routing)
    - Connected AX.25 with retransmission
    - Full KISS/XKISS support (standard, extended, polled 100ms, checksum, multi-drop)
    - AGWPE TCP/IP interface
    - NET/ROM level 3 support
    - Comprehensive logging and error handling
    - Production-grade (100% protocol coverage, robust error handling)
    - No encryption (by design - amateur radio plaintext)

    Licensed under **LGPL-3.0-or-later**.

    ## Installation

        pip install pyfbb

    ## Quick Example

        from pyfbb import FBBForwarder

        fwd = FBBForwarder(use_binary=True, enable_reverse=True)
        fwd.messages_to_send = [ ... ]
        fwd.connect("bbs.example.com", 6300, initiate_reverse=True)

    See examples/ for more.

    ## Documentation
    - AX.25 Integration Guide: docs/ax25_integration_guide.md
    - API Reference: Sphinx autodoc
    - Man page: man/pyfbb.3

    Version 0.1.2 — Current as of December 25, 2025
