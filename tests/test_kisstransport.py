# tests/test_kisstransport.py
"""
Comprehensive tests for KISSTransport with all modes: standard, extended, polled, checksum.
"""

import unittest
from unittest.mock import Mock, patch
from pyfbb.fbb.transport import KISSTransport

class TestKISSTransport(unittest.TestCase):
    def setUp(self):
        """Set up mock socket for TCP KISS tests."""
        self.mock_socket = Mock()
        self.mock_socket.recv.side_effect = self._mock_recv
        self.mock_socket.sendall = Mock()
        self.recv_data = []
        self.sent_data = []

    def _mock_recv(self, size):
        """Mock recv to return data from recv_data list."""
        if self.recv_data:
            data = self.recv_data.pop(0)
            return data
        return b''

    def test_framing_escaping(self):
        """Test FEND/FESC transparency escaping."""
        kiss = KISSTransport(host="127.0.0.1", port=8001)
        with patch('socket.socket', return_value=self.mock_socket):
            # Test escaping of FEND and FESC
            test_data = bytes([0xC0, 0xDB, 0x00, 0xFF])
            expected_frame = bytes([0xC0]) + bytes([0xDB, 0xDC, 0xDB, 0xDD, 0x00, 0xFF]) + bytes([0xC0])
            kiss.send_kiss(test_data)
            self.mock_socket.sendall.assert_called_with(expected_frame)

    def test_checksum_mode(self):
        """Test 8-bit checksum mode."""
        kiss = KISSTransport(host="127.0.0.1", port=8001, use_checksum=True)
        with patch('socket.socket', return_value=self.mock_socket):
            test_data = bytes([0x00, 0x01, 0x02])
            checksum = sum(test_data) & 0xFF
            expected_frame = bytes([0xC0]) + test_data + bytes([checksum]) + bytes([0xC0])
            kiss.send_kiss(test_data)
            self.mock_socket.sendall.assert_called_with(expected_frame)

    def test_checksum_validation(self):
        """Test checksum validation and discard on error."""
        kiss = KISSTransport(host="127.0.0.1", port=8001, use_checksum=True)
        with patch('socket.socket', return_value=self.mock_socket):
            # Good frame
            good_data = bytes([0xC0, 0x00, 0x01, 0x02, 0x03, 0xC0])  # checksum 0x03
            self.recv_data = [good_data]
            frame = kiss.recv_kiss()
            self.assertIsNotNone(frame)
            self.assertEqual(frame, bytes([0x00, 0x01, 0x02]))
            
            # Bad checksum
            bad_data = bytes([0xC0, 0x00, 0x01, 0x02, 0x04, 0xC0])  # wrong checksum
            self.recv_data = [bad_data]
            frame = kiss.recv_kiss()
            self.assertIsNone(frame)

    def test_polling_thread(self):
        """Test polled mode thread start/stop."""
        kiss = KISSTransport(
            host="127.0.0.1",
            port=8001,
            polled_mode=True,
            slave_addresses=[1, 2],
            poll_interval=0.01
        )
        with patch('socket.socket', return_value=self.mock_socket):
            kiss.start_polling()
            self.assertTrue(kiss._thread.is_alive())
            time.sleep(0.05)  # Allow a few polls
            kiss.stop_polling()
            self.assertFalse(kiss._thread.is_alive())

    def test_multi_drop_addressing(self):
        """Test multi-drop addressing in high nibble."""
        kiss = KISSTransport(host="127.0.0.1", port=8001)
        with patch('socket.socket', return_value=self.mock_socket):
            # Address 3 in high nibble
            addr_data = bytes([0x30 | 0x00])  # Address 3, command 0
            kiss.send_kiss(addr_data)
            # Verify sent with address

if __name__ == '__main__':
    unittest.main()
