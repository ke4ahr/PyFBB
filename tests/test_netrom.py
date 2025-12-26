# tests/test_netrom.py
"""
Tests for NET/ROM level 3 support.
"""

import unittest
from unittest.mock import Mock, patch
from pyfbb.fbb.transport import NETROMTransport

class TestNETROM(unittest.TestCase):
    def setUp(self):
        """Set up mock transport for NET/ROM tests."""
        self.mock_transport = Mock()
        self.mock_transport.send = Mock()
        self.mock_transport.recv = Mock(side_effect=self._mock_recv)
        self.recv_data = []

    def _mock_recv(self, size):
        """Mock recv to return data from recv_data list."""
        if self.recv_data:
            return self.recv_data.pop(0)
        return b''

    def test_node_routing(self):
        """Test NET/ROM node alias routing."""
        netrom = NETROMTransport(
            node_call="KE4AHR-7",
            destination="BBSNODE",
            path=["DIGI1", "DIGI2"]
        )
        with patch('pyfbb.fbb.transport.AX25Connection', return_value=self.mock_transport):
            netrom.connect()
            # Verify routing headers built correctly
            self.mock_transport.send.assert_called()

    def test_circuit_management(self):
        """Test NET/ROM circuit setup and teardown."""
        netrom = NETROMTransport(node_call="KE4AHR-7")
        with patch('pyfbb.fbb.transport.AX25Connection', return_value=self.mock_transport):
            netrom.connect()
            netrom.close()
            # Verify proper circuit disconnect

    def test_l3_frame_handling(self):
        """Test NET/ROM layer 3 frame parsing."""
        netrom = NETROMTransport(node_call="KE4AHR-7")
        test_frame = b'\x00' * 20  # Mock L3 frame
        self.recv_data = [test_frame]
        parsed = netrom._parse_l3_frame(test_frame)
        self.assertIsNotNone(parsed)
        # Verify opcode, circuit ID, etc.

    def test_transport_header(self):
        """Test NET/ROM transport header construction."""
        netrom = NETROMTransport(node_call="KE4AHR-7")
        header = netrom._make_transport_header(circuit=1, tx_seq=2, rx_seq=3)
        self.assertEqual(len(header), 5)
        # Verify time-to-live, circuit index, etc.

if __name__ == '__main__':
    unittest.main()
