FBB Forwarding Protocol and Winlink B2F Overview
================================================

:Date: December 25, 2025
:Author: Kris Kirby, KE4AHR
:Version: 0.1.2

FBB Forwarding Protocol
-----------------------

PyFBB provides complete implementation of the F6FBB packet radio BBS forwarding protocol.

**Core Features**:
- SID exchange with capability flags (F, B, B1, H, M, $)
- FA (ASCII), FB (binary LZHUF), FC (B2F block) proposals
- Full FS response handling (+ - = R H E)
- Reverse forwarding (FR command)
- Proposal checksum (M flag)
- Authentication (;PQ/;PR MD5)
- Multi-account forwarding (;FW)
- Resume support with offset handling
- XFWD extended forwarding
- Traffic limiting with H response

Winlink B2F Protocol
--------------------

PyFBB provides full compatibility with Winlink B2F extensions.

**Winlink-Specific Features**:
- FC B2F blocks with full headers (Mid, Date, Type, To/Cc, Subject, Mbo, Body, File)
- Winlink header validation
- Gzip compression option (experimental)
- Large attachment chunking
- RMS gateway routing behaviors

**Status**: 100% compatible with Winlink RMS gateways

References
----------

- F6FBB Forwarding Protocol Documentation
- Winlink B2F Specification
