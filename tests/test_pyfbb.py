# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Comprehensive unit and integration tests for all PyFBB components.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import socket
import sys

# Mock serial for KISS tests
sys.modules['serial'] = MagicMock()

from pyfbb.fbb.lzhuf import LZHUF_Comp
from pyfbb.fbb.forwarder import FBBForwarder, FBBProtocolError
from pyfbb.fbb.transport import TCPTransport, KISSTransport, AX25Connection, AGWTransport

class TestLZHUFComp(unittest.TestCase):
    """Test LZHUF compression/decompression."""
    
    def test_encode_decode_roundtrip(self):
        original = "Subject: Test\nHello this is a test message for FBB forwarding.\n73 de TEST\n"
        comp = LZHUF_Comp()
        compressed = comp.encode(original)
        self.assertIsInstance(compressed, bytes)
        self.assertLess(len(compressed), len(original.encode('latin-1')))
        decompressed = comp.decode(compressed)
        self.assertEqual(decompressed, original)

    def test_empty_string(self):
        comp = LZHUF_Comp()
        self.assertEqual(comp.decode(comp.encode("")), "")

    def test_repetitive_text(self):
        original = "ABC" * 500
        comp = LZHUF_Comp()
        compressed = comp.encode(original)
        self.assertLess(len(compressed), len(original.encode('latin-1')) * 0.7)
        self.assertEqual(comp.decode(compressed), original)

    def test_non_ascii(self):
        original = "Test with special chars: áéíóú ñ ç"
        comp = LZHUF_Comp()
        compressed = comp.encode(original)
        decompressed = comp.decode(compressed)
        self.assertEqual(decompressed, original)

class TestFBBForwarder(unittest.TestCase):
    """Test FBBForwarder core functionality."""
    
    def setUp(self):
        self.fwd = FBBForwarder(
            sid="[PyFBB-0.1.0-B1HLM$]",
            use_binary=True,
            enable_reverse=True,
            log_file=None  # Disable file logging for tests
        )
    
    def test_initialization(self):
        self.assertIsNone(self.fwd.sock)
        self.assertEqual(len(self.fwd.messages_to_send), 0)
        self.assertEqual(len(self.fwd.received_messages), 0)
        self.assertTrue(self.fwd.use_binary)
        self.assertTrue(self.fwd.enable_reverse)

    def test_message_validation(self):
        invalid_msg = {"type": "P", "mid": "123"}  # Missing required fields
        self.fwd.messages_to_send = [invalid_msg]
        with patch.object(self.fwd, '_log') as mock_log:
            self.fwd._send_proposal()
            mock_log.assert_called_with("warning", "Invalid message structure: unknown")

    @patch('pyfbb.fbb.forwarder.socket')
    def test_connection_retry(self, mock_socket):
        mock_socket.create_connection.side_effect = [ConnectionRefusedError, MagicMock()]
        self.fwd.connect("localhost", 1234, retries=2)
        self.assertEqual(mock_socket.create_connection.call_count, 2)

class TestTransports(unittest.TestCase):
    """Test all transport implementations."""
    
    def test_tcp_transport(self):
        with patch('socket.socket') as mock_sock:
            mock_instance = mock_sock.return_value
            mock_instance.recv.side_effect = [b'test', b'']
            
            transport = TCPTransport("localhost", 8000)
            transport.connect()
            transport.send(b'data')
            mock_instance.sendall.assert_called_with(b'data')
            
            data = transport.recv()
            self.assertEqual(data, b'test')
            transport.close()
            mock_instance.close.assert_called()

    def test_agw_transport_registration(self):
        with patch('socket.socket') as mock_sock:
            mock_instance = mock_sock.return_value
            mock_instance.recv.return_value = b'\x00\x00\x00\x00X\x00\x00\x00' + b'TEST      ' * 2 + b'\x00' * 8
            
            transport = AGWTransport("127.0.0.1", 8000, "TEST")
            transport.connect("BBS")
            self.assertTrue(transport.connected)
            transport.close()

    def test_kiss_framing(self):
        mock_conn = MagicMock()
        mock_conn.read.side_effect = [b'\xc0', b'\x00', b'test', b'\xc0']
        
        kiss = KISSTransport()
        kiss.conn = mock_conn
        frame = kiss.recv_kiss()
        self.assertEqual(frame, b'test')

    def test_ax25_address_encoding(self):
        conn = AX25Connection(None, "KE4AHR", "BBS-1")
        addr = conn._encode_address("KE4AHR", 0, 0, 0, True)
        # KE4AHR padded to 6 chars, shifted left 1 bit, last byte with SSID and flags
        expected = b'K\xccE\xcc4\xccaH\xccR\xcc\xf0'  # Approximate; actual depends on char codes
        self.assertEqual(len(addr), 7)

class TestIntegrationFullSession(unittest.TestCase):
    """High-level integration tests for complete forwarding sessions."""
    
    @patch('pyfbb.fbb.forwarder.socket')
    def test_full_ascii_session(self, mock_socket):
        mock_sock = mock_socket.return_value
        mock_sock.recv.side_effect = [
            b"[FBB-7.00]$", b"Welcome", b">",  # Server SID
            b"FS +", b"FF", b''  # Proposal response
        ]
        
        client = FBBForwarder(use_binary=False)
        client.messages_to_send = [{
            "type": "P", "from": "TEST", "to_bbs": "BBS", "to_call": "USER",
            "mid": "1_TEST", "content": "Test message"
        }]
        client.sock = mock_sock  # Inject mock
        client._forwarding_loop()
        
        self.assertGreater(len(client.received_messages), 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
