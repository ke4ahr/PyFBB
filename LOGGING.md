-----
evaluations/LOGGING.md
-----

    # Logging Coverage Evaluation for PyFBB (December 24, 2025)

    ## Overview

    PyFBB uses Python's standard `logging` module in `FBBForwarder` for session-level logging.

    ## Current Logging Coverage

    **Well Covered**:
    - Session start/close
    - Connection attempts (success/failure)
    - Proposal sending/receiving
    - FS response parsing
    - Message send/receive
    - Authentication events
    - Binary/ASCII mode selection
    - Error conditions (timeouts, invalid proposals, checksum errors)

    **Logging Levels Used**:
    - DEBUG: frame-level details
    - INFO: major events (connect, send, receive)
    - WARNING: non-fatal issues (rejected messages, reverse denied)
    - ERROR: protocol violations, decompression failures

    **File Logging**:
    - Optional log_file parameter writes to file with timestamps

    ## Gaps in Logging Coverage

    | Area                  | Missing Logging                                    | Severity |
    |-----------------------|----------------------------------------------------|----------|
    | KISSTransport         | No logging of raw frame send/receive               | Medium   |
    | KISSTransport         | Checksum mismatch (currently silent discard)       | Medium   |
    | KISSTransport         | Polling thread start/stop                          | Low      |
    | AX25Connection        | No logging of frame send/receive                   | High     |
    | AX25Connection        | Retransmission events (timeout, REJ, retry count)  | High     |
    | AX25Connection        | Link state changes (SABM, UA, DISC)                | High     |
    | LZHUF_Comp            | No logging on compression/decompression errors     | Low      |
    | AGWTransport          | No logging of AGWPE frames or connection state     | Medium   |
    | Overall               | No centralized logger configuration                | Low      |
    | Overall               | No structured logging (JSON) for machine parsing   | Low      |

    ## Recommendations

    - Add logging to all transport classes (KISS, AX.25, AGWPE)
    - Log retransmission events and link state changes
    - Make checksum mismatch a WARNING
    - Add debug logging for raw frames (optional, high volume)
    - Create a shared logger factory in __init__.py

    Current logging is good for high-level session monitoring but insufficient for low-level debugging of radio links.

    **Overall Rating**: 65% coverage — strong at protocol level, weak at transport/radio level.
