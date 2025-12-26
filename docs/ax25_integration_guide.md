
# AX.25 Integration Guide for PyFBB

**Date:** December 25, 2025  
**Author:** Kris Kirby, KE4AHR  
**Version:** 0.1.2  

## Introduction

PyFBB supports full AX.25 integration via KISS, XKISS, and AGWPE transports.

## XKISS (Extended KISS) Modes

PyFBB implements extended KISS (XKISS) modes for multi-drop and advanced TNC control:

- **Multi-drop addressing**: TNC address in high nibble of command byte (0-15)
- **Polled mode**: Master polling at 100ms interval using $xE command
- **Checksum mode**: 8-bit sum appended before FEND, validation with silent discard on mismatch
- **Parameter commands**: Full support for 0x01–0x06 (TXDelay, Persistence, SlotTime, TxTail, FullDuplex, Hardware)

See examples/quick_kiss.py for complete usage.

## AGWPE TCP/IP Interface

PyFBB supports the AGWPE TCP/IP socket interface for SoundCard TNC integration.

- **Connection**: Register with callsign on port 8000
- **Frame handling**: Full AGWPE frame header support (port, kind, callsigns, data length)
- **Monitoring**: Enable monitoring frames
- **Multiple ports**: Select radio port for transmission

See examples/quick_agwpe.py for complete usage.

## Usage Examples

    from pyfbb.fbb.transport import KISSTransport, AX25Connection
    from pyfbb import FBBForwarder

    kiss = KISSTransport(
        host="127.0.0.1",
        port=8001,
        use_checksum=True,
        polled_mode=True,
        slave_addresses=[1, 2]
    )

    ax25 = AX25Connection(kiss, "MYCALL", "BBS")
    fwd = FBBForwarder(ax25)
    fwd.connect()

See examples/ for complete scripts.
