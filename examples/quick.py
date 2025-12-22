from pyfbb import FBBForwarder

client = FBBForwarder(use_binary=True, enable_reverse=True)
client.messages_to_send = [
    {
        "type": "P",
        "from": "MYCALL",
        "to_bbs": "REMOTE",
        "to_call": "DEST",
        "mid": "123_MYCALL",
        "content": "Subject: Hello\n73 from PyFBB!\n"
    }
]
client.connect("bbs.example.com", 6300, initiate_reverse=True)
print("Received:", client.received_messages)
client.close()

