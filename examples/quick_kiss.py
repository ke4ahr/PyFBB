# examples/quick_kiss.py
"""
Example using KISS transport with extended features (multi-drop, polling, checksum).
"""

from pyfbb import FBBForwarder
from pyfbb.fbb.transport import KISSTransport, AX25Connection

# KISS over TCP (e.g., Dire Wolf or similar software TNC)
kiss = KISSTransport(
    host="127.0.0.1",
    port=8001,
    use_checksum=True,          # Enable 8-bit checksum mode
    polled_mode=True,           # Enable master polling
    slave_addresses=[1, 2, 3],  # Poll TNCs at addresses 1, 2, 3
    poll_interval=0.1           # 100ms polling interval
)

# AX.25 connection over the KISS transport
ax25 = AX25Connection(
    kiss=kiss,
    my_call="KE4AHR",
    remote_call="KE4AHR-1",
    path=[],
    window_size=4
)

# Create forwarder
fwd = FBBForwarder(
    transport=ax25,
    use_binary=True,
    enable_reverse=True,
    traffic_limit=1024 * 1024  # 1MB session limit
)

# Add a test message
fwd.add_message(
    msg_type="P",
    from_call="KE4AHR",
    to_bbs="KE4AHR-1",
    to_call="TESTUSER",
    mid="KISS001",
    content="This is a test message sent via extended KISS.\r\n"
            "Features: multi-drop, polling, checksum.\r\n"
            "73 de KE4AHR"
)

# Connect and forward
try:
    fwd.connect(initiate_reverse=True)
    print("KISS forwarding session completed successfully.")
    received = fwd.get_received_messages()
    print(f"Received {len(received)} messages.")
    for i, msg in enumerate(received, 1):
        print(f"Message {i}: {msg['content'][:100]}...")
except Exception as e:
    print(f"Forwarding failed: {e}")
