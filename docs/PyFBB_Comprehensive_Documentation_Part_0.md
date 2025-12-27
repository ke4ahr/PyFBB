# PyFBB Comprehensive Documentation - Part 0: Title and Table of Contents

**Version:** 0.1.2  
**Date:** December 26, 2025  
**Author:** Kris Kirby, KE4AHR  

## Title

PyFBB - Pure Python F6FBB Packet Radio BBS Forwarding Library

## Abstract

PyFBB is a production-grade pure Python implementation of the F6FBB packet radio BBS forwarding protocol with full Winlink B2F compatibility and AX.25 integration.

**Features:**
- Complete FBB protocol (resume, XFWD, traffic limiting, authentication)
- Full Winlink B2F support (gzip, large attachments, RMS routing)
- Full AX.25 connected mode with retransmission
- Complete KISS/XKISS (multi-drop, polled, checksum)
- AGWPE TCP/IP interface
- NET/ROM level 3 routing
- Comprehensive logging and error handling

## Table of Contents

- Part 0: Title and Table of Contents
- Part 1: Overview and Public API
- Part 2: Configuration, Error Handling, Logging
- Part 3: Threading, Concurrency, and Implementation Examples
- Part 4: Protocol Details and Advanced Features

## Introduction

PyFBB is designed as a library for building packet radio applications. It handles the complete FBB forwarding protocol stack from transport layer up to application layer.

The library is thread-safe and supports concurrent forwarding sessions.

All transports implement the common Transport interface for consistent usage.

## Quick Start

    from pyfbb import FBBForwarder
    from pyfbb.fbb.transport import TCPTransport

    transport = TCPTransport("bbs.example.com", 6300)
    fwd = FBBForwarder(transport)
    fwd.add_message("P", "MYCALL", "BBS", "USER", "MID001", "Hello")
    fwd.connect()
