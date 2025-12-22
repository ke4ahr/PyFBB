import sys
from pyfbb import FBBForwarder, LZHUFCompressor

def main():
    forwarder = FBBForwarder()
    compressor = LZHUFCompressor()
    try:
        forwarder.connect()
        forwarder.register_callsign('SERVERCALL')
        print("Server started. Monitoring...")
        data_frames = forwarder.monitor()
        for frame in data_frames:
            decompressed = compressor.decompress(frame)
            print(f"Received: {decompressed}")
            # Process and forward logic here
    except Exception as e:
        print(f"Error: {e}")
    finally:
        forwarder.close()

if __name__ == "__main__":
    main()
