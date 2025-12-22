# AX.25 Integration Guide for PyFBB

**Date:** December 22, 2025  
**Author:** Kris Kirby, KE4AHR  
**Version:** 0.1.0  

## Introduction

PyFBB is a pure-Python implementation of the classic **F6FBB** packet radio BBS forwarding protocol. It supports:

- ASCII and binary (LZHUF-compressed) forwarding modes
- Reverse forwarding (`FR` command)
- B2F extensions (multi-recipient, attachments, full headers)
- Authentication (`;PQ`/`;PR`) and multi-account (`;FW`)
- Multiple transport layers for real-world packet radio use

This guide focuses on **AX.25 integration** – connecting PyFBB to actual radio hardware via modern software TNCs using **KISS**, **XKISS**, or **AGWPE** protocols.

## Prerequisites

    pip install pyfbb
    # For serial KISS (hardware TNC or Mobilinkd):
    pip install pyserial

Recommended software TNCs:
- **Dire Wolf** (cross-platform, highly recommended)
- **UZ7HO SoundModem**
- **ldsped** (Linux)

## Transport Options

PyFBB supports three radio-capable transports:

- AGWPE TCP (port 8000) – legacy Windows AGW Packet Engine
- KISS/XKISS over TCP or serial – modern sound card TNCs
- Direct TCP (port 6300) – testing/local forwarding (no radio)

## 1. AGWPE Transport

    from pyfbb import FBBForwarder

    fwd = FBBForwarder(
        my_call="KE4AHR",
        remote_call="BBS-1",
        transport_type="agw",
        host="127.0.0.1",
        port=8000
    )

    fwd.connect()

## 2. KISS/XKISS Transport (Recommended)

### TCP KISS (Dire Wolf)

    from pyfbb.fbb.transport import KISSTransport, AX25Connection
    from pyfbb import FBBForwarder

    kiss = KISSTransport(host="127.0.0.1", port=8001)

    ax25 = AX25Connection(
        kiss=kiss,
        my_call="KE4AHR",
        remote_call="BBSNODE",
        path=["WIDE1-1", "WIDE2-1"]
    )

    fwd = FBBForwarder(transport=ax25)
    fwd.connect()

### Serial KISS

    kiss = KISSTransport(serial_port="/dev/ttyUSB0", baud=9600)

    ax25 = AX25Connection(kiss=kiss, my_call="KE4AHR", remote_call="BBSNODE")

    fwd = FBBForwarder(transport=ax25)
    fwd.connect()

## 3. Direct TCP (Testing)

    fwd = FBBForwarder(transport_type="tcp", host="remote.bbs.example", port=6300)
    fwd.connect()

## Frame Handling Details

- AGWPE: 36-byte headers (Port, DataKind, CallFrom/CallTo, DataLen)
- KISS: Simple `\xC0` framing with escaping
- AX.25 Connected Mode: SABM/UA connect, I-frames, RR polling

## Troubleshooting

- Verify TNC is listening on the correct port
- Use `netstat -an` to check connections
- Enable logging: `FBBForwarder(log_file="fbb_debug.log")`

## References

- F6FBB Forwarding Protocol Documentation
- AGWPE TCP/IP API Tutorial (LU7DID/SV2AGW, 2000)
- Dire Wolf User Guide
- AX.25 Protocol Specification
