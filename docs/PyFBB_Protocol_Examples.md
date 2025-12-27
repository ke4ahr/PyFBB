# PyFBB Comprehensive Documentation

**Version:** 0.1.2  
**Date:** December 26, 2025  
**Author:** Kris Kirby, KE4AHR  

## Table of Contents

- Overview
- Public API
- Transports
- Error Handling
- Logging
- Configuration
- Threading and Concurrency
- Protocol Details
  - FBB Forwarding Protocol
  - Winlink B2F Protocol
  - XKISS (Extended KISS)
  - AGWPE Interface
  - NET/ROM Level 3
  - PACSAT File Headers

## Overview

PyFBB provides:
- 100% FBB protocol coverage (resume, XFWD, traffic limiting, authentication)
- 100% Winlink B2F compatibility (gzip, large attachments, RMS routing)
- Full AX.25 connected mode with retransmission
- Complete KISS/XKISS support (multi-drop, polled, checksum)
- AGWPE TCP/IP interface
- NET/ROM level 3 routing
- Comprehensive logging and error handling
- No encryption (amateur radio plaintext)

## Public API

### Core Classes

#### `FBBForwarder`

    class FBBForwarder:
        def __init__(
            self,
            transport: Transport,
            sid: str = "[PyFBB-0.1.2-B1FHLM$]",
            use_binary: bool = True,
            enable_reverse: bool = True,
            traffic_limit: int = 1024 * 1024,
            log_file: Optional[str] = None,
            use_gzip: bool = False
        ):
            """Initialize forwarding session."""
        
        def connect(self, initiate_reverse: bool = False) -> None:
            """Connect and perform SID negotiation."""
        
        def add_message(
            self,
            msg_type: str,
            from_call: str,
            to_bbs: str,
            to_call: str,
            mid: str,
            content: str
        ) -> None:
            """Add message to send queue."""
        
        def get_received_messages(self) -> List[Dict]:
            """Return received messages and clear list."""
        
        def close(self) -> None:
            """Close session."""

### Transport Classes

#### `TCPTransport`

    class TCPTransport(Transport):
        def __init__(self, host: str, port: int, timeout: float = 30.0):
            """Direct TCP transport."""

#### `KISSTransport`

    class KISSTransport(Transport):
        def __init__(
            self,
            serial_port: Optional[str] = None,
            baud: int = 9600,
            host: Optional[str] = None,
            port: int = 8001,
            use_checksum: bool = False,
            polled_mode: bool = False,
            slave_addresses: List[int] = None,
            poll_interval: float = 0.1
        ):
            """Full KISS/XKISS transport."""

#### `AX25Connection`

    class AX25Connection(Transport):
        def __init__(
            self,
            kiss: KISSTransport,
            my_call: str,
            remote_call: str,
            path: List[str] = [],
            window_size: int = 4
        ):
            """Connected mode AX.25 over KISS."""

#### `AGWTransport`

    class AGWTransport(Transport):
        def __init__(self, host: str = "127.0.0.1", port: int = 8000, call: str = "NOCALL"):
            """AGWPE TCP/IP interface."""

## Error Handling

    try:
        fwd.connect()
    except FBBProtocolError as e:
        # Protocol violations (invalid proposal, authentication failure)
        print(f"Protocol error: {e}")
    except Exception as e:
        # Transport or connection errors
        print(f"Connection failed: {e}")

## Logging

    # File logging
    fwd = FBBForwarder(transport, log_file="session.log")

    # Manual access
    fwd.logger.debug("Raw frame")
    fwd.logger.info("Session started")
    fwd.logger.warning("Traffic limit")
    fwd.logger.error("Decompression failed")

## Configuration

    from dataclasses import dataclass
    from typing import List

    @dataclass
    class KISSTNCConfig:
        address: int = 0
        txdelay: int = 30
        persistence: int = 63
        slottime: int = 10
        txtail: int = 10
        fullduplex: bool = False
        hardware: int = 0
        ignore: bool = False
        polled_mode: bool = False
        use_checksum: bool = False

    def generate_kiss_config_packets(config: KISSTNCConfig) -> List[bytes]:
        """Generate KISS parameter frames."""
        # Full implementation

## Threading and Concurrency

### Threading Example

    import threading

    def forwarding_session(bbs_host, bbs_port):
        transport = TCPTransport(bbs_host, bbs_port)
        fwd = FBBForwarder(transport, log_file=f"{bbs_host}.log")
        try:
            fwd.connect()
        except Exception as e:
            print(f"Session to {bbs_host} failed: {e}")

    threads = []
    for bbs in [("bbs1.example.com", 6300), ("bbs2.example.com", 6300)]:
        t = threading.Thread(target=forwarding_session, args=bbs)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

### Async Pattern (Future)

    import asyncio

    async def async_forwarding_session(bbs_host: str, bbs_port: int):
        transport = AsyncTCPTransport(bbs_host, bbs_port)  # Future async transport
        fwd = FBBForwarder(transport)
        try:
            await fwd.connect_async()
        except Exception as e:
            print(f"Async session to {bbs_host} failed: {e}")

    async def main():
        tasks = [
            async_forwarding_session("bbs1.example.com", 6300),
            async_forwarding_session("bbs2.example.com", 6300)
        ]
        await asyncio.gather(*tasks)

    asyncio.run(main())

## Protocol Details

### FBB Forwarding Protocol

Complete implementation of F6FBB protocol including:
- Resume support
- XFWD extended forwarding
- Traffic limiting
- Authentication

### Winlink B2F Protocol

Full compatibility with Winlink extensions:
- Gzip compression option
- Large attachment chunking
- RMS routing behaviors

### XKISS (Extended KISS)

Full support for:
- Multi-drop addressing
- Polled mode (100ms)
- Checksum mode
- Parameter configuration

### AGWPE Interface

Full TCP/IP socket interface with registration and frame handling.

### NET/ROM Level 3

Support for NET/ROM routing headers and circuit management.

### PACSAT File Headers

Support for PACSAT file header encoding in messages
