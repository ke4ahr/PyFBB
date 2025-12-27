# PyFBB Comprehensive Documentation - Part 4: Protocol Details and Advanced Features

**Version:** 0.1.2  
**Date:** December 26, 2025  
**Author:** Kris Kirby, KE4AHR  

## Protocol Details

### FBB Forwarding Protocol

Complete implementation of F6FBB protocol including:
- Resume support with offset handling
- XFWD extended forwarding capability exchange
- Traffic limiting with H response
- Authentication with MD5 challenge-response

### Winlink B2F Protocol

Full compatibility with Winlink extensions:
- Gzip compression option
- Large attachment chunking
- RMS gateway routing behaviors
- Full header validation (Mid, Date, Type, To, From, Subject)

### XKISS (Extended KISS)

Full support for:
- Multi-drop addressing (0-15)
- Polled mode (100ms master polling)
- Checksum mode (8-bit sum)
- Parameter configuration (TXDelay, Persistence, SlotTime, TxTail, FullDuplex, Hardware)

### AGWPE Interface

Full TCP/IP socket interface with:
- Registration (R frame) and confirmation (X frame)
- Frame header support (port, kind, callsigns, data length)
- Monitoring mode
- Multiple radio ports

### NET/ROM Level 3

Support for:
- Node routing with aliases
- Circuit management
- Transport header (5 bytes)
- Inter-node HDLC frames

### PACSAT File Headers

Support for PACSAT file header encoding in messages:
- Optional, Mandatory, Extended headers
- 2-byte item ID
- Length and data fields

## Advanced Usage Examples

### Resume Support with Offset Handling

    # Client side - detect partial transfer and resume
    # Store offset locally
    resume_offset = 1024  # From previous session

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="BBS",
        to_call="USER",
        mid="RESUME001",
        content="Large message content..."
    )

    # Proposal will include @offset syntax
    # Server accepts with +
    # Client sends from stored offset

### XFWD Extended Forwarding

    fwd = FBBForwarder(
        transport=transport,
        sid="[PyFBB-0.1.2-B1FHLMX$]"  # Include X flag for XFWD
    )

    fwd.connect()  # Extended capabilities negotiated automatically

### Traffic Limiting Enforcement

    fwd = FBBForwarder(
        transport=transport,
        traffic_limit=50000  # 50KB limit
    )

    # Add many messages
    for i in range(20):
        fwd.add_message(
            msg_type="P",
            from_call="MYCALL",
            to_bbs="BBS",
            to_call="USER",
            mid=f"LIMIT{i}",
            content="X" * 3000
        )

    fwd.connect()  # Server responds with H for excess messages

### Authentication with MD5 Challenge-Response

    # Handled transparently by FBBForwarder
    # Server sends ;PQ challenge
    # Client automatically responds with ;PR MD5 hash
    # Using configured shared secret

### Winlink B2F with Gzip and Large Attachment Chunking

    fwd = FBBForwarder(
        transport=transport,
        use_binary=True,
        use_gzip=True
    )

    large_content = "A" * 150000  # 150KB attachment

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="RMS",
        to_call="USER",
        mid="B2F001",
        content=f"Mid: B2F001\r\nDate: 2025-12-26\r\nType: P\r\nTo: USER\r\nFrom: MYCALL\r\nSubject: Large B2F\r\n{large_content}"
    )

    fwd.connect()  # Automatic gzip compression and chunking
