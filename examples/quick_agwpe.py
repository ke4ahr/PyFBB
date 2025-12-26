# examples/quick_agwpe.py
"""
Example using AGWPE transport for SoundCard TNC integration.
"""

from pyfbb import FBBForwarder
from pyfbb.fbb.transport import AGWTransport, AX25Connection

# Connect to AGWPE (typically running on same machine)
agw = AGWTransport(
    host="127.0.0.1",
    port=8000,
    call="KE4AHR"  # Your callsign for registration
)

# AX.25 connection over AGWPE
ax25 = AX25Connection(
    kiss=agw,  # AGWTransport implements KISS-like interface
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
    mid="AGW001",
    content="This is a test message sent via AGWPE transport.\r\n"
            "Using SoundCard TNC integration.\r\n"
            "73 de KE4AHR"
)

# Connect and forward
try:
    fwd.connect(initiate_reverse=True)
    print("AGWPE forwarding session completed successfully.")
    received = fwd.get_received_messages()
    print(f"Received {len(received)} messages.")
    for i, msg in enumerate(received, 1):
        print(f"Message {i}: {msg['content'][:100]}...")
except Exception as e:
    print(f"Forwarding failed: {e}")
