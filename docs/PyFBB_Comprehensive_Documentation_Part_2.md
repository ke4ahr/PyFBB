# PyFBB Comprehensive Documentation - Part 2: Configuration, Error Handling, Logging

**Version:** 0.1.2  
**Date:** December 26, 2025  
**Author:** Kris Kirby, KE4AHR  

## Configuration

### Configuration Structure

    from dataclasses import dataclass
    from typing import List, Optional

    @dataclass
    class KISSTNCConfig:
        address: int = 0
        txdelay: int = 30          # 300 ms
        persistence: int = 63      # ~25%
        slottime: int = 10         # 100 ms
        txtail: int = 10
        fullduplex: bool = False
        hardware: int = 0
        ignore: bool = False
        polled_mode: bool = False
        use_checksum: bool = False

    @dataclass
    class PyFBBConfig:
        sid: str = "[PyFBB-0.1.2-B1FHLM$]"
        use_binary: bool = True
        enable_reverse: bool = True
        traffic_limit: int = 1024 * 1024
        use_gzip: bool = False
        log_file: Optional[str] = None
        kiss_tncs: Optional[List[KISSTNCConfig]] = None

### Configuration Functions

    def generate_kiss_config_packets(config: KISSTNCConfig) -> List[bytes]:
        """Generate KISS parameter frames for TNC configuration."""
        if config.ignore:
            return []
        
        packets = []
        # TXDelay (0x01)
        packets.append(bytes([0x01, config.txdelay]))
        # Persistence (0x02)
        packets.append(bytes([0x02, config.persistence]))
        # SlotTime (0x03)
        packets.append(bytes([0x03, config.slottime]))
        # TxTail (0x04)
        packets.append(bytes([0x04, config.txtail]))
        # FullDuplex (0x05)
        packets.append(bytes([0x05, 0x01 if config.fullduplex else 0x00]))
        # Hardware (0x06)
        packets.append(bytes([0x06, config.hardware]))
        return packets

### Configuration Loading Example

    import json
    from dataclasses import asdict

    def load_config(file_path: str) -> PyFBBConfig:
        """Load configuration from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return PyFBBConfig(**data)

    # Example config.json
    # {
    #   "sid": "[MyBBS-0.1.2-B1FHLM$]",
    #   "traffic_limit": 2097152,
    #   "use_gzip": true,
    #   "log_file": "forwarding.log"
    # }

## Error Handling

### Exception Hierarchy

    class FBBError(Exception):
        """Base exception for all PyFBB errors."""

    class FBBProtocolError(FBBError):
        """Protocol-level errors (invalid proposal, authentication failure)."""

    class TransportError(FBBError):
        """Transport-level errors (timeout, disconnect)."""

    class ConfigError(FBBError):
        """Configuration errors."""

### Error Handling Example

    try:
        fwd.connect()
    except FBBProtocolError as e:
        # Protocol violations
        print(f"Protocol error: {e}")
        # Log and continue or retry
    except TransportError as e:
        # Connection issues
        print(f"Transport error: {e}")
        # Attempt reconnection
    except Exception as e:
        # Unexpected errors
        print(f"Unexpected error: {e}")
        # Log for debugging

## Logging

### Logging Configuration

    import logging

    # Basic logging setup
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler("pyfbb.log"),
            logging.StreamHandler()
        ]
    )

    # In FBBForwarder
    fwd = FBBForwarder(transport, log_file="session.log")

    # Direct logger access
    fwd.logger.debug("Raw frame received")
    fwd.logger.info("Session started")
    fwd.logger.warning("Traffic limit approaching")
    fwd.logger.error("Decompression failed")

### Thread-Safe Logging Example

    import threading

    def forwarding_session(bbs_host, bbs_port):
        transport = TCPTransport(bbs_host, bbs_port)
        fwd = FBBForwarder(transport, log_file=f"{bbs_host}.log")
        try:
            fwd.connect()
        except Exception as e:
            fwd.logger.error(f"Session failed: {e}")

    # Multiple concurrent sessions with separate log files
