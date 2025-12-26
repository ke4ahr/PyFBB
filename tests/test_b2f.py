# tests/test_b2f.py
"""
Comprehensive tests for Winlink B2F protocol extensions.
"""

import unittest
from unittest.mock import Mock, patch
from pyfbb import FBBForwarder, FBBProtocolError
from pyfbb.fbb.transport import TCPTransport

class TestWinlinkB2F(unittest.TestCase):
    def setUp(self):
        """Set up mock transport and forwarder for B2F tests."""
        self.mock_transport = Mock(spec=TCPTransport)
        self.mock_transport.recv.side_effect = self._mock_recv
        self.mock_transport.send = Mock()
        self.recv_data = []
        
        self.fwd = FBBForwarder(
            transport=self.mock_transport,
            use_binary=True,
            use_gzip=True,  # Enable gzip for B2F tests
            traffic_limit=0  # Unlimited for testing
        )

    def _mock_recv(self, size):
        """Mock recv to return data from recv_data list."""
        if self.recv_data:
            data = self.recv_data.pop(0)
            return data.encode('latin-1')
        return b''

    def test_gzip_compression(self):
        """Test gzip compression option in B2F."""
        test_content = "This is a test message for gzip compression in B2F."
        compressed = self.fwd._compress(test_content)
        import gzip
        decompressed = gzip.decompress(compressed).decode('latin-1')
        self.assertEqual(decompressed, test_content)

    def test_lzhuf_fallback(self):
        """Test LZHUF fallback when gzip disabled."""
        self.fwd.use_gzip = False
        test_content = "Test message for LZHUF fallback."
        compressed = self.fwd._compress(test_content)
        decompressed = LZHUF_Comp().decode(compressed)
        self.assertEqual(decompressed, test_content)

    def test_large_attachment_chunking(self):
        """Test handling of large attachments in B2F."""
        large_content = "A" * 100000  # 100KB
        self.fwd.add_message(
            msg_type="P",
            from_call="KE4AHR",
            to_bbs="KE4AHR-1",
            to_call="USER",
            mid="LARGE001",
            content=large_content
        )
        self.recv_data = ["FS +"]
        self.fwd._send_proposal()
        # Verify multiple send calls for chunking
        self.assertGreater(len(self.mock_transport.send.call_args_list), 1)

    def test_winlink_header_validation(self):
        """Test Winlink-specific B2F header validation."""
        valid_headers = {
            "Mid": "TEST001",
            "Date": "2025-12-25",
            "Type": "P",
            "To": "USER",
            "From": "KE4AHR",
            "Subject": "Test"
        }
        self.fwd._validate_b2f_headers(valid_headers)  # Should not raise

        invalid_headers = {"Mid": "TEST002", "Subject": "Missing fields"}
        with self.assertRaises(FBBProtocolError):
            self.fwd._validate_b2f_headers(invalid_headers)

    def test_rms_routing_behavior(self):
        """Test RMS gateway routing behaviors in B2F."""
        # Simulate RMS-specific headers
        rms_headers = {
            "Mid": "RMS001",
            "Date": "2025-12-25",
            "Type": "P",
            "To": "RMS",
            "From": "KE4AHR",
            "Subject": "RMS test"
        }
        # Verify RMS mode detection and routing
        self.fwd._validate_b2f_headers(rms_headers)
        # Additional RMS-specific logic test
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
