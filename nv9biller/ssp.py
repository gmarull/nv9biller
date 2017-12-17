BAUDRATE = 9600
""" int: Baudrate (bps). """
TIMEOUT = 1
""" int: Timeout (s). """

CRC_POLY = 0x18005
""" int: CRC polynomial (CRC16-IBM). """
CRC_INIT = 0xFFFF
""" int: CRC initialization value. """
CRC_LEN = 2
""" int: CRC length (bytes). """

STX = 0x7F
""" int: STX (start) byte value. """
SEQ = 0x80
""" int: Sequence flag. """

RESP_FLD = 2
""" int: Response code byte in the response. """

ERR_OK = 0xF0
""" int: Error code, OK. """
ERR_NOTKNOWN = 0xF2
""" int: Error code, command not known. """
ERR_NOPARAM = 0xF3
""" int: Error code, incorrect number of parameters. """
ERR_RANGE = 0xF4
""" int: Error code, one of the parameters is out of range. """
ERR_PROCESS = 0xF5
""" int: Error code, command could not be processed. """
ERR_SW = 0xF6
""" int: Error code, software error. """
ERR_FAIL = 0xF8
""" int: Error code, general failure. """
ERR_KEY = 0xFA
""" int: Error code, encryption keys not negotiated. """

ERR_DESC = {ERR_NOTKNOWN: 'Command not known',
            ERR_NOPARAM: 'Incorrect number of parameters',
            ERR_RANGE: 'One of the parameters is out of range',
            ERR_PROCESS: 'Command could not be processed',
            ERR_SW: 'Software error',
            ERR_FAIL: 'General failure',
            ERR_KEY: 'Encryption keys not negotiated'}
""" dict: Error codes descriptions. """

CMD_CH_INHIBITS = 0x02
""" int: Command, channel inhibits. """
CMD_DISP_EN = 0x03
""" int: Command, display enable. """
CMD_DISP_DIS = 0x04
""" int: Command, display disable. """
CMD_SETUP_REQ = 0x05
""" int: Command, setup request. """
CMD_POLL = 0x07
""" int: Command, poll. """
CMD_REJECT = 0x08
""" int: Command, reject. """
CMD_DISABLE = 0x09
""" int: Command, disable. """
CMD_ENABLE = 0x0A
""" int: Command, enable. """
CMD_GET_SERIAL = 0x0C
""" int: Command, get serial. """
CMD_SYNC = 0x11
""" int: Command, sync. """
CMD_HOLD = 0x18
""" int: Command, hold. """
CMD_COUNTERS_GET = 0x58
""" int: Command, counters get. """
CMD_COUNTERS_RST = 0x59
""" int: Command, counters reset. """

EVT_RESET = 0xF1
""" int: Event, reset. """
EVT_READ = 0xEF
""" int: Event, read. """
EVT_CREDIT = 0xEE
""" int: Event, credit. """
EVT_REJECTING = 0xED
""" int: Event, rejecting. """
EVT_REJECTED = 0xEC
""" int: Event, rejected. """
EVT_STACKING = 0xCC
""" int: Event, stacking. """
EVT_STACKED = 0xEB
""" int: Event, stacked. """
EVT_SAFE_JAM = 0xEA
""" int: Event, safe jam. """
EVT_UNSAFE_JAM = 0xE9
""" int: Event, unsafe jam. """
EVT_DISABLED = 0xE8
""" int: Event, disabled. """
EVT_STACKER_FULL = 0xE7
""" int: Event, stacker full. """
EVT_CLEARED_FRONT = 0xE1
""" int: Event, cleared to front. """
EVT_CLEARED_CASHBOX = 0xE2
""" int: Event, cleared to cashbox. """
EVT_CH_DISABLE = 0xB5
""" int: Event, channel disable. """
EVT_INITIALIZING = 0xB6
""" int: Event, initializing. """
EVT_TICKET_BEZEL = 0xAD
""" int: Event, ticket in bezel. """
EVT_PRINTED_CASHBOX = 0xAF
""" int: Event, printed to cashbox. """

EVT_ALL = (EVT_RESET, EVT_READ, EVT_CREDIT, EVT_REJECTING, EVT_REJECTED,
           EVT_STACKING, EVT_STACKED, EVT_SAFE_JAM, EVT_UNSAFE_JAM,
           EVT_DISABLED, EVT_STACKER_FULL, EVT_CLEARED_FRONT,
           EVT_CLEARED_CASHBOX, EVT_CH_DISABLE, EVT_INITIALIZING,
           EVT_TICKET_BEZEL, EVT_PRINTED_CASHBOX)
""" tuple: All events. """
