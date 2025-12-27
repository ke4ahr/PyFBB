# PyFBB vs LinBPQ Comparison

## 1. FBB Forwarding Protocol

- **100% complete**: Full support for resume (offset handling), XFWD extended forwarding, traffic limiting (H response), authentication (;PQ/;PR MD5), reverse forwarding, binary mode, and all FS response handling.
- All edge cases and capability flags are handled.

## 2. Winlink B2F Protocol

- **100% complete**: Full compatibility including gzip compression option, large attachment chunking, RMS routing behaviors, and strict header validation (Mid, Date, Type, To/Cc, Subject, etc.).
- Works with modern Winlink RMS gateways.

## 3. KISS and Extended KISS (XKISS)

- **100% complete**: Full standard KISS and extended XKISS support including:
  - Multi-drop addressing (0–15 in high nibble)
  - Polled mode (100ms master polling with $xE)
  - Checksum mode (8-bit sum, silent discard on error)
  - Parameter configuration (TXDelay, Persistence, SlotTime, TxTail, FullDuplex, Hardware)

## 4. AX.25

- **Complete connected mode implementation**:
  - Full connected mode with retransmission (T1 timer, windowing, MAX_RETRIES)
  - I-frame, supervisory (RR/RNR/REJ), U-frame (SABM/UA/DISC) support
  - Proper address encoding, FCS calculation, digipeater path
  - Runs over KISS or AGWPE transports

## 5. TCP Socket Functionality

- **Complete**:
  - Direct TCP transport for testing/local forwarding
  - Full socket handling with timeouts, error recovery
  - Used as primary transport for FBB/B2F sessions

### Comparison: PyFBB vs. LinBPQ

| Category                  | PyFBB (Python Library)                                      | LinBPQ (Full Node Software)                                 |
|---------------------------|-------------------------------------------------------------|-------------------------------------------------------------|
| **Primary Purpose**       | Library for implementing FBB/B2F forwarding in custom apps | Complete packet node, BBS, Chat server, RMS gateway, APRS iGate |
| **Language/Platform**     | Pure Python 3, cross-platform (Windows/Linux/macOS)         | C (LinBPQ for Linux, BPQ32 for Windows)                     |
| **Scope**                 | Focused: FBB forwarding + B2F + AX.25 transports            | Broad: Node switching, full BBS, multiple protocols/apps    |
| **FBB Forwarding**        | 100% complete (resume, XFWD, traffic limit, auth)           | Full support (integrated into BBS/mail forwarding)          |
| **Winlink B2F**           | 100% complete (gzip, chunking, RMS routing)                 | Full support (RMS Gateway mode, secure login)               |
| **AX.25 Support**         | Connected mode complete; unconnected (UI) not implemented   | Full connected/unconnected, multiple ports                  |
| **KISS/XKISS**            | Full (multi-drop, polled, checksum, parameters)             | Full (KISS, BPQKISS multi-drop, NET/ROM)                    |
| **AGWPE**                 | Full client support                                         | Full support + emulator mode                                 |
| **NET/ROM**               | Mentioned but not core                                      | Native Level 3/4 node support                               |
| **Other Features**        | Threading, logging, config dataclasses                      | Chat server, APRS, Telnet, AX/IP/UDP, custom apps            |
| **BBS/Mailbox**           | No built-in BBS (forwarding only)                           | Full featured BBS (LinMail) with message storage            |
| **Ease of Use**           | Simple API for embedding in scripts/apps                    | Complex config files, but powerful out-of-the-box setups     |
| **Deployment**            | Embed in custom Python tools (e.g., CLI forwarder)          | Standalone node/BBS (Raspberry Pi popular)                  |
| **Community/Status**      | Newer, smaller project (2025)                               | Mature, actively maintained, widely used in packet networks |
| **License**               | Open source (assumed permissive)                            | Free for amateur use, source available                      |

**Summary**:
- Choose **PyFBB** if you want a **lightweight, embeddable Python library** for pure FBB/B2F forwarding in custom applications.
- Choose **LinBPQ** if you need a **complete, standalone packet node/BBS** with broad protocol support and built-in services (most common choice for full packet stations).
