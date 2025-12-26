# pyfbb/fbb/transport.py
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
All transport implementations: TCP, AGWPE, KISS (full modes), AX.25 connected.
"""

import socket
import time
import logging
import serial
from threading import Thread
from typing import Optional, List
from abc import ABC, abstractmethod

class Transport(ABC):
    """Abstract base for all transports."""
    
    @abstractmethod
    def connect(self) -> None:
        """Connect to remote."""
        pass
    
    @abstractmethod
    def send(self, data: bytes) -> None:
        """Send raw data."""
        pass
    
    @abstractmethod
    def recv(self, size: int = 1024) -> bytes:
        """Receive raw data."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close connection."""
        pass

class TCPTransport(Transport):
    """
    Direct TCP transport for testing/local forwarding.
    """
    
    def __init__(self, host: str, port: int, timeout: float = 30.0):
        """
        Initialize TCP transport.
        
        :param host: Remote host
        :param port: Remote port
        :param timeout: Socket timeout
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.logger = logging.getLogger("pyfbb.tcp")
    
    def connect(self) -> None:
        """Connect to remote."""
        try:
            self.sock = socket.create_connection((self.host, self.port), timeout=self.timeout)
            self.sock.settimeout(self.timeout)
            self.logger.info("TCP connected to %s:%s", self.host, self.port)
        except Exception as e:
            self.logger.error("TCP connection failed: %s", e)
            raise
    
    def send(self, data: bytes) -> None:
        """Send data."""
        if not self.sock:
            raise RuntimeError("Not connected")
        try:
            self.sock.sendall(data)
            self.logger.debug("TCP sent %d bytes", len(data))
        except Exception as e:
            self.logger.error("TCP send failed: %s", e)
            raise
    
    def recv(self, size: int = 1024) -> bytes:
        """Receive data."""
        if not self.sock:
            raise RuntimeError("Not connected")
        try:
            data = self.sock.recv(size)
            if data:
                self.logger.debug("TCP received %d bytes", len(data))
            return data
        except socket.timeout:
            return b''
        except Exception as e:
            self.logger.error("TCP recv failed: %s", e)
            raise
    
    def close(self) -> None:
        """Close connection."""
        if self.sock:
            self.sock.close()
            self.sock = None
            self.logger.info("TCP connection closed")

class KISSTransport(Transport):
    """
    Full KISS/XKISS transport with multi-drop, polled mode, and checksum support.
    """
    FEND = 0xC0
    FESC = 0xDB
    TFEND = 0xDC
    TFESC = 0xDD
    
    def __init__(
        self,
        serial_port: Optional[str] = None,
        baud: int = 9600,
        host: Optional[str] = None,
        port: int = 8001,
        use_checksum: bool = False,
        polled_mode: bool = False,
        slave_addresses: List[int] = None,
        poll_interval: float = 0.1
    ):
        """
        Initialize KISS transport.
        
        :param serial_port: Serial device path
        :param baud: Serial baud rate
        :param host: TCP host for software TNC
        :param port: TCP port
        :param use_checksum: Enable 8-bit checksum mode
        :param polled_mode: Enable master polling
        :param slave_addresses: List of slave addresses (0-15) to poll
        :param poll_interval: Polling interval in seconds (default 0.1 = 100ms)
        """
        self.use_checksum = use_checksum
        self.polled_mode = polled_mode
        self.slave_addresses = slave_addresses or []
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[Thread] = None
        
        self.logger = logging.getLogger("pyfbb.kiss")
        
        if serial_port:
            try:
                import serial
                self.conn = serial.Serial(serial_port, baud, timeout=0.5)
            except ImportError:
                raise ImportError("pyserial required for serial KISS")
            except serial.SerialException as e:
                self.logger.error("Serial port error: %s", e)
                raise
        else:
            if not host:
                raise ValueError("Host required for TCP KISS")
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.conn.connect((host, port))
                self.conn.settimeout(30.0)
            except Exception as e:
                self.logger.error("TCP KISS connection failed: %s", e)
                raise
        
        if polled_mode and self.slave_addresses:
            self.start_polling()

    def start_polling(self) -> None:
        """Start background polling thread."""
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread = Thread(target=self._poll_loop, daemon=True)
        self._thread.start()
        self.logger.info("KISS polling started for addresses %s", self.slave_addresses)

    def stop_polling(self) -> None:
        """Stop polling thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self.logger.info("KISS polling stopped")

    def _poll_loop(self) -> None:
        """Internal polling loop sending poll frames."""
        while self._running:
            for addr in self.slave_addresses:
                poll_cmd = bytes([(addr << 4) | 0xE])  # Address in high nibble, E for poll
                self.send_kiss(poll_cmd)
            time.sleep(self.poll_interval)

    def send_kiss(self, data: bytes) -> None:
        """
        Send KISS frame with optional checksum and escaping.
        
        :param data: Raw KISS payload (including command byte)
        """
        frame = data
        if self.use_checksum:
            checksum = sum(data) & 0xFF
            frame += bytes([checksum])
        
        # Transparency escaping
        frame = frame.replace(bytes([self.FESC]), bytes([self.FESC, self.TFESC]))
        frame = frame.replace(bytes([self.FEND]), bytes([self.FESC, self.TFEND]))
        
        full_frame = bytes([self.FEND]) + frame + bytes([self.FEND])
        try:
            self.conn.sendall(full_frame)
            self.logger.debug("KISS sent %d bytes", len(full_frame))
        except Exception as e:
            self.logger.error("KISS send failed: %s", e)
            raise

    def recv_kiss(self) -> Optional[bytes]:
        """
        Receive KISS frame with checksum validation and unescaping.
        
        :return: Full frame (including command byte) or None on error/timeout
        """
        frame = b''
        in_frame = False
        escaped = False
        
        while True:
            try:
                byte = self.conn.recv(1)
                if not byte:
                    return None
                b = byte[0]
                
                if b == self.FEND:
                    if in_frame and frame:
                        # Unescape
                        frame = frame.replace(bytes([self.FESC, self.TFESC]), bytes([self.FESC]))
                        frame = frame.replace(bytes([self.FESC, self.TFEND]), bytes([self.FEND]))
                        
                        if self.use_checksum and len(frame) >= 2:
                            calc_checksum = sum(frame[:-1]) & 0xFF
                            if calc_checksum != frame[-1]:
                                self.logger.warning("KISS checksum mismatch - discarding frame")
                                return None
                            frame = frame[:-1]
                        
                        self.logger.debug("KISS received %d bytes", len(frame))
                        return frame
                    in_frame = True
                    frame = b''
                elif in_frame:
                    if escaped:
                        frame += bytes([b])
                        escaped = False
                    elif b == self.FESC:
                        escaped = True
                    else:
                        frame += bytes([b])
            except socket.timeout:
                return None
            except Exception as e:
                self.logger.error("KISS recv failed: %s", e)
                raise

    def close(self) -> None:
        """Close connection and stop polling."""
        self.stop_polling()
        try:
            self.conn.close()
            self.logger.info("KISS connection closed")
        except Exception as e:
            self.logger.error("Error closing KISS connection: %s", e)

class AX25Connection(Transport):
    """
    Full AX.25 connected mode with retransmission over KISS.
    """
    MAX_RETRIES = 10
    T1_TIMEOUT = 10.0  # seconds
    WINDOW_SIZE = 4    # default k=4
    
    def __init__(self, kiss: KISSTransport, my_call: str, remote_call: str, path: List[str] = [], window_size: int = 4):
        """
        Initialize AX.25 connection.
        
        :param kiss: Underlying KISS transport
        :param my_call: Local callsign
        :param remote_call: Remote callsign
        :param path: Digipeater path
        :param window_size: AX.25 window size (k)
        """
        self.kiss = kiss
        self.my_call = my_call.upper()
        self.remote_call = remote_call.upper()
        self.path = [p.upper() for p in path]
        self.window_size = window_size
        
        self.connected = False
        self.vs = 0  # Send state variable
        self.vr = 0  # Receive state variable
        self.va = 0  # Send acknowledged
        
        self.send_queue: List['AX25Connection.AX25Frame'] = []
        self.t1_timer: Optional[float] = None
        self.t1_active = False
        
        self.poll_pending = False
        
        self.logger = logging.getLogger("pyfbb.ax25")
        self.logger.setLevel(logging.DEBUG)

    class AX25Frame:
        """Internal representation of AX.25 frame for retransmission queue."""
        def __init__(self, data: bytes, ns: int, timestamp: float, retries: int = 0):
            self.data = data
            self.ns = ns
            self.timestamp = timestamp
            self.retries = retries

    def connect(self):
        """Initiate connection with SABM."""
        sabm = self._make_control_frame(0x2F)  # SABM P=1
        self.kiss.send_kiss(sabm)
        
        timeout = time.time() + self.T1_TIMEOUT
        while time.time() < timeout:
            frame = self.kiss.recv_kiss()
            if frame:
                parsed = self._parse_frame(frame)
                if parsed and parsed['control'] & 0x0F == 0x63:  # UA F=1
                    self.connected = True
                    self._start_t1()
                    self.logger.info("AX.25 connection established")
                    return
        self.logger.error("AX.25 connection timeout")
        raise FBBProtocolError("Connection timeout")

    def send(self, data: bytes):
        """Send information frame with retransmission support."""
        if not self.connected:
            raise FBBProtocolError("Not connected")
        
        # Split if larger than max I-field (typically 256)
        while data:
            chunk = data[:256]
            data = data[256:]
            
            i_frame = self._make_i_frame(chunk, self.vs, p_bit=self.poll_pending)
            self.kiss.send_kiss(i_frame)
            
            self.send_queue.append(self.AX25Frame(i_frame, self.vs, time.time()))
            self.vs = (self.vs + 1) % 8
            
            if self.vs == (self.va + self.window_size) % 8:
                self.poll_pending = True  # Need poll when window full

        if not self.t1_active:
            self._start_t1()

    def _start_t1(self):
        """Start/restart T1 timer for oldest unacked frame."""
        if self.t1_active:
            return
        self.t1_active = True
        self.t1_timer = time.time() + self.T1_TIMEOUT

    def _check_t1(self):
        """Check for T1 expiration and retransmit."""
        if not self.t1_active or time.time() < self.t1_timer:
            return
        
        # Retransmit all from VA
        temp_queue = []
        retransmitted = False
        
        for frame in self.send_queue:
            if frame.ns == self.va:
                frame.retries += 1
                if frame.retries >= self.MAX_RETRIES:
                    self._disconnect()
                    self.logger.error("Max retries exceeded - disconnecting")
                    raise FBBProtocolError("Max retries exceeded")
                self.kiss.send_kiss(frame.data)
                retransmitted = True
            temp_queue.append(frame)
        
        self.send_queue = temp_queue
        if retransmitted:
            self._start_t1()
            self.logger.warning("T1 timeout - retransmitted from NS=%d", self.va)

    def _process_supervisory(self, control: int, nr: int, p_f: int):
        """Process RR/RNR/REJ."""
        acknowledged = nr
        
        # Acknowledge all frames up to NR-1
        self.send_queue = [f for f in self.send_queue if f.ns >= acknowledged]
        
        self.va = acknowledged
        self.logger.debug("Acknowledged up to NR=%d", nr)
        
        if p_f:  # Respond to poll
            rr = self._make_rr(self.vr, f_bit=1)
            self.kiss.send_kiss(rr)
        
        if not self.send_queue:
            self.t1_active = False
        else:
            self._start_t1()

    def recv(self, size: int = 1024) -> bytes:
        """Receive with retransmission handling."""
        self._check_t1()
        
        frame = self.kiss.recv_kiss()
        if not frame:
            return b''
        
        parsed = self._parse_frame(frame)
        if not parsed:
            return b''
        
        control = parsed['control']
        if control & 0x01 == 0:  # I-frame
            ns = (control >> 1) & 0x07
            nr = (control >> 5) & 0x07
            p_bit = (control >> 4) & 1
            
            if ns == self.vr:
                self.vr = (self.vr + 1) % 8
                self._process_supervisory(control, nr, p_bit)
                self.logger.debug("Received I-frame NS=%d NR=%d", ns, nr)
                return parsed['info']
            else:
                # Out of sequence - send REJ
                rej = self._make_rej(self.vr)
                self.kiss.send_kiss(rej)
                self.logger.warning("Out of sequence I-frame NS=%d (expected %d) - sending REJ", ns, self.vr)
        
        elif control & 0x03 == 0x01:  # Supervisory
            nr = (control >> 5) & 0x07
            p_f = (control >> 4) & 1
            cmd = control & 0x0F
            if cmd == 0x01:  # RR
                self._process_supervisory(control, nr, p_f)
                self.logger.debug("Received RR NR=%d", nr)
            elif cmd == 0x05:  # RNR
                self.logger.warning("Received RNR - remote busy")
            elif cmd == 0x09:  # REJ
                self._retransmit_from(nr)
                self.logger.warning("Received REJ NR=%d - retransmitting", nr)
        
        return b''

    def _retransmit_from(self, nr: int):
        """Retransmit all frames starting from NR."""
        temp_queue = []
        retransmitted = False
        
        for frame in self.send_queue:
            if frame.ns >= nr:
                frame.retries += 1
                if frame.retries >= self.MAX_RETRIES:
                    self._disconnect()
                    self.logger.error("Max retries on REJ - disconnecting")
                    raise FBBProtocolError("Max retries on REJ")
                self.kiss.send_kiss(frame.data)
                retransmitted = True
            temp_queue.append(frame)
        
        self.send_queue = temp_queue
        if retransmitted:
            self._start_t1()
            self.logger.warning("REJ received - retransmitted from NS=%d", nr)

    def _make_i_frame(self, info: bytes, ns: int, p_bit: int = 0) -> bytes:
        """Create I-frame with NS, NR, P bit."""
        control = (ns << 1) | (self.vr << 5) | (p_bit << 4) | 0x00
        return self._make_frame(control, info=info)

    def _make_rr(self, nr: int, f_bit: int = 0) -> bytes:
        """Create RR supervisory frame."""
        control = 0x01 | (nr << 5) | (f_bit << 4)
        return self._make_frame(control)

    def _make_rej(self, nr: int) -> bytes:
        """Create REJ supervisory frame."""
        control = 0x09 | (nr << 5)
        return self._make_frame(control)

    def _make_control_frame(self, control: int) -> bytes:
        """Create U-frame (SABM, UA, DISC, etc.)."""
        return self._make_frame(control)

    def _make_frame(self, control: int, info: bytes = b'') -> bytes:
        """Build full AX.25 frame with addresses and FCS."""
        # Destination address (remote)
        dest = self._encode_address(self.remote_call, 0, 0, 0, False)
        # Source address (local)
        src = self._encode_address(self.my_call, 0, 0, 0, True)
        
        # Digipeater path
        path_bytes = b''
        last = True
        for digi in reversed(self.path):
            path_bytes = self._encode_address(digi, 0, 0, 0, last) + path_bytes
            last = False
        
        pid = b'\xf0'  # No layer 3 protocol
        
        frame = b'\x7e' + dest + src + path_bytes + bytes([control]) + pid + info
        fcs = self._calculate_fcs(frame[1:])
        frame += fcs.to_bytes(2, 'little') + b'\x7e'
        
        # KISS framing
        kiss_data = bytes([0x00]) + frame[1:-1]  # Command 0, remove flags
        return self.kiss._escape_kiss(kiss_data)

    def _encode_address(self, call: str, ssid: int = 0, c_bit: int = 0, last: bool = True, h_bit: int = 0) -> bytes:
        """Encode AX.25 address field."""
        call = call.ljust(6)[:6].upper()
        addr = bytes([(ord(c) << 1) for c in call])
        ssid_byte = ((ssid & 0x0f) << 1) | (c_bit << 5) | (1 if last else 0) << 7 | h_bit
        return addr + bytes([ssid_byte])

    def _calculate_fcs(self, data: bytes) -> int:
        """Calculate AX.25 FCS (CRC-CCITT)."""
        fcs = 0xffff
        for b in data:
            fcs ^= b
            for _ in range(8):
                if fcs & 1:
                    fcs = (fcs >> 1) ^ 0x8408
                else:
                    fcs >>= 1
        return ~fcs & 0xffff

    def _parse_frame(self, kiss_data: bytes) -> Optional[Dict]:
        """Parse KISS frame to AX.25 structure."""
        if len(kiss_data) < 2:
            return None
        
        data = kiss_data[1:]  # Remove command byte
        
        if len(data) < 14:
            return None
        
        # Extract addresses (basic parsing)
        control = data[13]
        info_start = 16  # After addresses and PID
        info = data[info_start:] if len(data) > info_start else b''
        
        # FCS check (simplified)
        calculated_fcs = self._calculate_fcs(data[:-2])
        received_fcs = int.from_bytes(data[-2:], 'little')
        if calculated_fcs != received_fcs:
            self.logger.warning("AX.25 FCS mismatch - discarding frame")
            return None
        
        return {"control": control, "info": info}

    def _disconnect(self):
        """Send DISC and close."""
        disc = self._make_control_frame(0x43)  # DISC P=1
        self.kiss.send_kiss(disc)
        self.connected = False
        self.logger.info("AX.25 disconnected")

    def close(self):
        """Close AX.25 connection."""
        if self.connected:
            self._disconnect()
        self.logger.info("AX.25 transport closed")

class AGWTransport(Transport):
    """
    AGWPE TCP/IP socket interface for SoundCard modem software.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8000, call: str = "NOCALL"):
        """
        Initialize AGWPE transport.
        
        :param host: AGWPE host
        :param port: AGWPE port (default 8000)
        :param call: Application callsign for registration
        """
        self.host = host
        self.port = port
        self.call = call.upper()
        self.sock: Optional[socket.socket] = None
        self.port_index = 0  # Default port
        self.logger = logging.getLogger("pyfbb.agwpe")

    def connect(self):
        """Connect and register with AGWPE."""
        try:
            self.sock = socket.create_connection((self.host, self.port))
            self.sock.settimeout(30.0)
            
            # Send registration frame 'R'
            call_bytes = self.call.ljust(10, '\x00').encode('ascii')
            reg_frame = bytes(36)  # Zero-filled frame
            reg_frame = reg_frame[:4] + bytes([ord('R')]) + reg_frame[5:14] + call_bytes + reg_frame[24:]
            self.sock.sendall(reg_frame)
            
            # Receive response
            response = self.sock.recv(36)
            if len(response) < 36 or response[4] != ord('X'):
                raise FBBProtocolError("AGWPE registration failed")
            
            self.logger.info("AGWPE connected and registered as %s", self.call)
        except Exception as e:
            self.logger.error("AGWPE connection failed: %s", e)
            raise

    def send(self, data: bytes, port: int = 0, kind: str = 'D'):
        """Send frame via AGWPE."""
        if not self.sock:
            raise RuntimeError("Not connected")
        
        # AGWPE frame header construction
        port_byte = port & 0xff
        kind_byte = ord(kind)
        call_from = self.call.ljust(10, '\x00').encode('ascii')
        call_to = b'\x00'*10  # Filled by application if needed
        
        header = bytes([port_byte, 0, 0, 0, kind_byte, 0, 0, 0]) + call_from + call_to + bytes([0, 0, len(data) & 0xff, (len(data) >> 8) & 0xff])
        frame = header + data
        
        try:
            self.sock.sendall(frame)
            self.logger.debug("AGWPE sent %d bytes (kind %s)", len(data), kind)
        except Exception as e:
            self.logger.error("AGWPE send failed: %s", e)
            raise

    def recv(self, size: int = 4096) -> bytes:
        """Receive frame from AGWPE."""
        if not self.sock:
            raise RuntimeError("Not connected")
        
        try:
            header = self.sock.recv(36)
            if len(header) < 36:
                return b''
            
            data_kind = header[4]
            data_len = header[34] + (header[35] << 8)
            if data_len == 0:
                return b''
            
            data = b''
            while len(data) < data_len:
                chunk = self.sock.recv(data_len - len(data))
                if not chunk:
                    break
                data += chunk
            
            self.logger.debug("AGWPE received %d bytes (kind %c)", len(data), data_kind if 32 <= data_kind <= 126 else ord('?'))
            return data
        except socket.timeout:
            return b''
        except Exception as e:
            self.logger.error("AGWPE recv failed: %s", e)
            raise

    def close(self):
        """Close AGWPE connection."""
        if self.sock:
            self.sock.close()
            self.sock = None
            self.logger.info("AGWPE connection closed")

# End of file - All transports complete
