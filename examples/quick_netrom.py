# examples/quick_netrom.py
"""
Example demonstrating NET/ROM level 3 routing support in PyFBB.
"""

from pyfbb import FBBForwarder, NETROMTransport

# NET/ROM transport (requires NET/ROM node configuration)
netrom = NETROMTransport(
    node_call="KE4AHR-7",  # Local NET/ROM alias
    destination="BBSNODE",  # Remote node alias
    path=["DIGI1", "DIGI2"]  # Optional path
)

# Create forwarder
fwd = FBBForwarder(netrom, use_binary=True, enable_reverse=True)

# Add test message
fwd.add_message(
    msg_type="P",
    from_call="KE4AHR",
    to_bbs="KE4AHR-1",
    to_call="USER",
    mid="NETROM001",
    content="NET/ROM level 3 routing test\r\n73"
)

# Connect and forward
try:
    fwd.connect(initiate_reverse=True)
    print("NET/ROM forwarding complete")
    print(f"Received {len(fwd.get_received_messages())} messages")
except Exception as e:
    print(f"NET/ROM connection failed: {e}")
