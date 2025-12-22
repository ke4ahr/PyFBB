# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Unit and integration tests for PyFBB.
"""

import unittest
from threading import Thread
import time

from pyfbb import FBBForwarder, FBBProtocolError
from pyfbb.fbb.lzhuf import LZHUF_Comp

class TestLZHUFCompression(unittest.TestCase):
    def test_round_trip(self):
        original = "Subject: Test\nHello from PyFBB!\n73 de TEST\n"
        compressed = LZHUF_Comp().encode(original)
        self.assertLess(len(compressed), len(original.encode()))
        decompressed = LZHUF_Comp().decode(compressed)
        self.assertEqual(decompressed, original)

    def test_empty(self):
        self.assertEqual(LZHUF_Comp().decode(LZHUF_Comp().encode("")), "")

class TestFBBFullSession(unittest.TestCase):
    PORT = 8002

    @classmethod
    def setUpClass(cls):
        cls.server_msgs = [{"type": "P", "from": "SERVER", "mid": "1_SERVER", "content": "From server\n"}]
        cls.client_msgs = [{"type": "P", "from": "CLIENT", "mid": "1_CLIENT", "content": "From client\n"}]

    def run_server(self, use_binary=False, allow_reverse=False):
        server = FBBForwarder(use_binary=use_binary, enable_reverse=allow_reverse)
        server.messages_to_send = self.server_msgs.copy()
        server.listen(self.PORT, allow_reverse=allow_reverse)
        server.close()

    def test_ascii_session(self):
        Thread(target=self.run_server).start()
        time.sleep(0.5)
        client = FBBForwarder()
        client.messages_to_send = self.client_msgs.copy()
        client.connect("localhost", self.PORT)
        self.assertGreater(len(client.received_messages), 0)
        client.close()

    def test_reverse_forwarding(self):
        Thread(target=self.run_server, args=(True, True)).start()
        time.sleep(0.5)
        client = FBBForwarder(use_binary=True, enable_reverse=True)
        client.messages_to_send = self.client_msgs.copy()
        client.connect("localhost", self.PORT, initiate_reverse=True)
        self.assertGreater(len(client.received_messages), 0)
        client.close()

if __name__ == "__main__":
    unittest.main()

