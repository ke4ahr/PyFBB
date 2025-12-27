# PyFBB Comprehensive Documentation - Part 3: Threading, Concurrency, and Complete Implementation Examples

**Version:** 0.1.2  
**Date:** December 26, 2025  
**Author:** Kris Kirby, KE4AHR  

## Threading and Concurrency

### Threading Example (Multiple Concurrent Sessions)

    import threading

    def forwarding_session(bbs_host: str, bbs_port: int):
        transport = TCPTransport(bbs_host, bbs_port)
        fwd = FBBForwarder(
            transport=transport,
            log_file=f"{bbs_host}.log",
            traffic_limit=2 * 1024 * 1024
        )
        fwd.add_message(
            msg_type="P",
            from_call="MYCALL",
            to_bbs="REMOTEBBS",
            to_call="USER",
            mid="THREAD001",
            content="Threaded session test\r\n73"
        )
        try:
            fwd.connect()
            print(f"Session to {bbs_host} completed")
        except Exception as e:
            print(f"Session to {bbs_host} failed: {e}")

    threads = []
    bbs_list = [("bbs1.example.com", 6300), ("bbs2.example.com", 6300)]
    for bbs in bbs_list:
        t = threading.Thread(target=forwarding_session, args=bbs)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

### Async Pattern (Future Implementation)

    import asyncio

    async def async_forwarding_session(bbs_host: str, bbs_port: int):
        # Future async transport
        transport = AsyncTCPTransport(bbs_host, bbs_port)
        fwd = FBBForwarder(transport)
        try:
            await fwd.connect_async()
            print(f"Async session to {bbs_host} completed")
        except Exception as e:
            print(f"Async session to {bbs_host} failed: {e}")

    async def main():
        tasks = [
            async_forwarding_session("bbs1.example.com", 6300),
            async_forwarding_session("bbs2.example.com", 6300)
        ]
        await asyncio.gather(*tasks)

    asyncio.run(main())

## Complete Implementation Examples

### Basic TCP Forwarding with Error Handling

    from pyfbb import FBBForwarder
    from pyfbb.fbb.transport import TCPTransport

    transport = TCPTransport(host="bbs.example.com", port=6300, timeout=60.0)

    fwd = FBBForwarder(
        transport=transport,
        use_binary=True,
        enable_reverse=True,
        traffic_limit=2 * 1024 * 1024,
        log_file="tcp_session.log"
    )

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="REMOTEBBS",
        to_call="USER",
        mid="TCP001",
        content="Basic TCP forwarding test\r\n73"
    )

    try:
        fwd.connect(initiate_reverse=True)
        print("Forwarding completed")
        for msg in fwd.get_received_messages():
            print(f"Received MID: {msg.get('mid', 'unknown')}")
            print(msg['content'])
    except FBBProtocolError as e:
        print(f"Protocol error: {e}")
    except Exception as e:
        print(f"Transport error: {e}")
    finally:
        fwd.close()

### Extended KISS with Multi-Drop, Polling, Checksum and Logging

    from pyfbb import FBBForwarder
    from pyfbb.fbb.transport import KISSTransport, AX25Connection

    kiss = KISSTransport(
        host="127.0.0.1",
        port=8001,
        use_checksum=True,
        polled_mode=True,
        slave_addresses=[1, 2, 3],
        poll_interval=0.1
    )

    ax25 = AX25Connection(
        kiss=kiss,
        my_call="MYCALL",
        remote_call="BBS-1",
        path=["DIGI1"],
        window_size=6
    )

    fwd = FBBForwarder(
        transport=ax25,
        use_binary=True,
        log_file="kiss_session.log"
    )

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="BBS-1",
        to_call="USER",
        mid="KISS001",
        content="Extended KISS test with polling and checksum\r\n73"
    )

    try:
        fwd.connect()
        print("KISS forwarding completed")
    except Exception as e:
        print(f"KISS error: {e}")
    finally:
        fwd.close()

### AGWPE Integration with Monitoring

    from pyfbb import FBBForwarder
    from pyfbb.fbb.transport import AGWTransport, AX25Connection

    agw = AGWTransport(
        host="127.0.0.1",
        port=8000,
        call="MYCALL"
    )

    ax25 = AX25Connection(
        kiss=agw,
        my_call="MYCALL",
        remote_call="BBS-1"
    )

    fwd = FBBForwarder(ax25, log_file="agwpe.log")

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="BBS-1",
        to_call="USER",
        mid="AGW001",
        content="AGWPE SoundCard TNC integration test\r\n73"
    )

    try:
        fwd.connect()
        print("AGWPE forwarding completed")
    except Exception as e:
        print(f"AGWPE error: {e}")

### NET/ROM Level 3 Routing

    from pyfbb import FBBForwarder
    from pyfbb.fbb.transport import NETROMTransport

    netrom = NETROMTransport(
        node_call="MYCALL-7",
        destination="BBSNODE",
        path=["DIGI1", "DIGI2"]
    )

    fwd = FBBForwarder(netrom, use_binary=True)

    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="BBSNODE",
        to_call="USER",
        mid="NETROM001",
        content="NET/ROM level 3 routing test\r\n73"
    )

    try:
        fwd.connect()
        print("NET/ROM forwarding completed")
    except Exception as e:
        print(f"NET/ROM error: {e}")

### Resume Support with Offset Handling

    # Client side - detect partial transfer and resume
    fwd.add_message(
        msg_type="P",
        from_call="MYCALL",
        to_bbs="BBS",
        to_call="USER",
        mid="RESUME001",
        content="Large message content..."
    )

    # In proposal, use @offset syntax
    # Server accepts with +
    # Client sends from stored offset

### XFWD Extended Forwarding

    fwd = FBBForwarder(
        transport=transport,
        sid="[PyFBB-0.1.2-B1FHLMX$]"
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

    # Server sends ;PQ challenge
    # Client automatically responds with ;PR MD5 hash
    # Handled transparently by FBBForwarder

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
