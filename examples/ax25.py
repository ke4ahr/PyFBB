from pyfbb import FBBForwarder

forwarder = FBBForwarder()
forwarder.connect()
forwarder.register_callsign('LU7DID')
forwarder.send_data(b'Hello AX.25!', callsign_from='LU7DID', callsign_to='SV2AGW')
forwarder.close()
