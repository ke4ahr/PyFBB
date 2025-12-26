# examples/quick_tcp.py
"""
Simple example using direct TCP transport for testing/local forwarding.
"""

from pyfbb import FBBForwarder
from pyfbb.fbb.transport import TCPTransport

# Create TCP transport to a local FBB server or test endpoint
transport = TCPTransport(
    host="127.0.0.1",
    port=6300,
    timeout=30.0
)

# Create forwarder with binary mode enabled
fwd = FBBForwarder(
    transport=transport,
    use_binary=True,
    enable_reverse=True,
    traffic_limit=1024 * 1024  # 1MB session limit
)

# Add a test message to the send queue
fwd.add_message(
    msg_type="P",               # Personal message
    from_call="KE4AHR",
    to_bbs="KE4AHR-1",
    to_call="TESTUSER",
    mid="TCPTEST001",
    content="This is a test message sent via direct TCP transport.\r\n"
            "PyFBB quick_tcp.py example.\r\n"
            "73 de KE4AHR"
)

# Connect and perform forwarding
try:
    fwd.connect(initiate_reverse=True)
    print("TCP forwarding session completed successfully.")
    received = fwd.get_received_messages()
    print(f"Received {len(received)} messages during session.")
    for i, msg in enumerate(received, 1):
        print(f"Message {i}: {msg['content'][:100]}...")
except Exception as e:
    print(f"Forwarding failed: {e}")
