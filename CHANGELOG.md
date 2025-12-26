    # PyFBB Changelog

    ## [0.1.2] - 2025-12-25

    ### Added
    - Full FBB resume support with offset handling
    - XFWD extended forwarding capability exchange
    - Traffic limiting with H response generation
    - Full Winlink B2F compatibility (gzip compression option, large attachment chunking, RMS routing behaviors)
    - Comprehensive logging for all new features
    - Error handling for edge cases in resume, XFWD, traffic limit, B2F
    - Comprehensive unit and integration tests for all new features
    - Updated documentation with new features and examples

    ## [0.1.1] - 2025-12-24

    ### Added
    - Broad SID compatibility (accepts any bracketed SID, not just [FBB-*])
    - Internal tooling improvements
    - Documentation enhancements

    ## [0.1.0] - 2025-12-23

    ### Added
    - Initial release with core FBB forwarding protocol
    - LZHUF compression implementation
    - Full AX.25 transport layers (KISS with polled/checksum/multi-drop, AGWPE)
    - NET/ROM level 3 support
    - Comprehensive error handling and session logging
    - Complete unit/integration test suite
    - Full documentation with multiple examples
