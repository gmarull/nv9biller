import time
import serial
import crcmod
from struct import pack, unpack

from . import ssp


__version__ = '0.1.0'


class BillerCommunicationsError(Exception):
    """ Biller Communications Error. """
    pass


class BillerChannel(object):
    """ Biller channel.

        Args:
            value (int, float): Value (multiplied).
            currency (str): Currency code.
    """

    def __init__(self, value, currency):
        self._value = value
        self._currency = currency

    def __str__(self):
        return '{:.02f} {}'.format(self._value, self._currency)

    @property
    def value(self):
        """ int, float: Value. """
        return self._value

    @property
    def currency(self):
        """ str: Currency. """
        return self._currency


class BillerEvent(object):
    """ Biller event.

        Args:
            code (int): Code.
            channel (BillerChannel, optional): Channel.
    """

    _EVT_DESC = {ssp.EVT_RESET: 'Reset',
                 ssp.EVT_READ: 'Read',
                 ssp.EVT_CREDIT: 'Credit',
                 ssp.EVT_REJECTING: 'Rejecting',
                 ssp.EVT_REJECTED: 'Rejected',
                 ssp.EVT_STACKING: 'Stacking',
                 ssp.EVT_STACKED: 'Stacked',
                 ssp.EVT_SAFE_JAM: 'Safe jam',
                 ssp.EVT_UNSAFE_JAM: 'Unsafe jam',
                 ssp.EVT_DISABLED: 'Disabled',
                 ssp.EVT_STACKER_FULL: 'Stacker full',
                 ssp.EVT_CLEARED_FRONT: 'Cleared to front',
                 ssp.EVT_CLEARED_CASHBOX: 'Cleared to cashbox',
                 ssp.EVT_CH_DISABLE: 'Channels disabled',
                 ssp.EVT_INITIALIZING: 'Initializing',
                 ssp.EVT_TICKET_BEZEL: 'Ticket in bezel',
                 ssp.EVT_PRINTED_CASHBOX: 'Printed to cashbox'}
    """ dict: Event descriptions. """

    def __init__(self, code, channel=None):
        self._code = code
        self._channel = channel

    def __str__(self):
        fmt = '{}'.format(self._EVT_DESC[self._code])
        if self._channel:
            fmt += ' -> {}'.format(str(self._channel))

        return fmt

    @property
    def code(self):
        """ int: Code. """
        return self._code

    @property
    def channel(self):
        """ BillerChannel: Channel. """
        return self._channel


class Biller(object):
    """ Biller (NV9USB).

        Args:
            port (str): Serial port.

         References:
            Innovative Technology SSP Protocol manual (GA183)
    """

    (_RX_STATE_WAIT_STX, _RX_STATE_WAIT_SEQ, _RX_STATE_WAIT_LEN,
     _RX_STATE_WAIT_DATA, _RX_STATE_WAIT_CRC, _RX_STATE_FINISHED) = range(6)
    """ tuple: Reception states. """

    (CH_0, CH_1, CH_2, CH_3, CH_4, CH_5, CH_6, CH_7, CH_8, CH_9, CH_10, CH_11,
     CH_12, CH_13, CH_14, CH_15) = range(16)
    """ tuple: Channels. """

    CH_ALL = (CH_0, CH_1, CH_2, CH_3, CH_4, CH_5, CH_6, CH_7, CH_8, CH_9,
              CH_10, CH_11, CH_12, CH_13, CH_14, CH_15)
    """ tuple: All channels. """

    (EVT_RESET, EVT_READ, EVT_CREDIT, EVT_REJECTING, EVT_REJECTED,
     EVT_STACKING, EVT_STACKED, EVT_SAFE_JAM, EVT_UNSAFE_JAM, EVT_DISABLED,
     EVT_STACKER_FULL, EVT_CLEARED_FRONT, EVT_CLEARED_CASHBOX, EVT_CH_DISABLE,
     EVT_INITIALIZING, EVT_TICKET_BEZEL, EVT_PRINTED_CASHBOX) = ssp.EVT_ALL
    """ tuple: Event codes. """

    def __init__(self, port):
        self._s = serial.Serial(port, ssp.BAUDRATE, timeout=ssp.TIMEOUT)
        self._crc = crcmod.mkCrcFun(ssp.CRC_POLY, rev=False,
                                    initCrc=ssp.CRC_INIT)

        self._sequence = 0
        self._sync()
        self._load_settings()

    def _send(self, command, data=b''):
        """ Send a request.

            Args:
                command (int): Command code.
                data (bytes): Data payload.
        """

        # package command and data
        pkt = pack('BBB', self._sequence, 1 + len(data), command) + data

        # compute and append CRC
        pkt += pack('<H', self._crc(pkt))

        # add stx and stuff
        stx = pack('B', ssp.STX)
        pkt = stx + pkt.replace(stx, stx + stx)

        self._s.write(pkt)

    def _recv(self):
        """ Receive the response of a request.

            Raises:
                BillerCommunicationsError: If there is a communication error.

            Returns:
                bytes: Response payload.
        """

        pkt = b''
        pkt_counter = 0
        state = self._RX_STATE_WAIT_STX
        init = time.time()

        while state != self._RX_STATE_FINISHED:
            if time.time() - init > ssp.TIMEOUT:
                raise BillerCommunicationsError('Timeout')

            data = self._s.read()
            if not data:
                continue

            # wait until STX
            if state == self._RX_STATE_WAIT_STX:
                if unpack('B', data)[0] == ssp.STX:
                    state = self._RX_STATE_WAIT_SEQ
            else:
                # skip stuffed bytes
                if unpack('B', data)[0] == ssp.STX:
                    continue

                pkt += data

                # process state
                if state == self._RX_STATE_WAIT_SEQ:
                    state = self._RX_STATE_WAIT_LEN
                elif state == self._RX_STATE_WAIT_LEN:
                    pkt_len = unpack('B', data)[0]
                    state = self._RX_STATE_WAIT_DATA
                elif state == self._RX_STATE_WAIT_DATA:
                    pkt_counter += 1
                    if pkt_counter == pkt_len:
                        pkt_counter = 0
                        state = self._RX_STATE_WAIT_CRC
                elif state == self._RX_STATE_WAIT_CRC:
                    pkt_counter += 1
                    if pkt_counter == ssp.CRC_LEN:
                        state = self._RX_STATE_FINISHED

        # validate CRC
        crc = self._crc(pkt[:-ssp.CRC_LEN])
        if crc != unpack('<H', pkt[-ssp.CRC_LEN:])[0]:
            raise BillerCommunicationsError('CRC mismatch')

        # check for response errors
        err = pkt[ssp.RESP_FLD]
        if err != ssp.ERR_OK:
            raise BillerCommunicationsError(ssp.ERR_DESC[err])

        return pkt[ssp.RESP_FLD + 1:-ssp.CRC_LEN]

    def _transmit(self, command, data=b''):
        """ Send a request.

            Args:
                command (int): Command code.
                data (bytes): Data payload.

            Raises:
                BillerCommunicationsError: If there is a communication error.

            Returns:
                bytes: Response payload.
        """

        self._send(command, data)
        r = self._recv()

        self._sequence ^= ssp.SEQ

        return r

    def _sync(self):
        """ Synchronize communications. """

        self._transmit(ssp.CMD_SYNC)
        self._sequence = 0

    def _load_settings(self):
        """ Load settings """

        # request serial
        r = self._transmit(ssp.CMD_GET_SERIAL)
        self._serial = unpack('>I', r)[0]

        # request setup
        s = self._transmit(ssp.CMD_SETUP_REQ)

        self._fw_version = s[1:1 + 4].decode('utf8')

        # process each channel information
        n_ch = s[11]
        multiplier = unpack('>I', b'\x00' + s[8:8 + 3])[0]

        self._channels = []

        for ch in range(n_ch):
            off = 12 + ch
            value = s[off] * multiplier

            off = 16 + n_ch * 2 + ch * 3
            currency = s[off:off + 3].decode('utf8')

            self._channels.append(BillerChannel(value, currency))

    @property
    def serial(self):
        """ int: Serial number. """
        return self._serial

    @property
    def fw_version(self):
        """ str: Firmware version. """
        return self._fw_version

    @property
    def channels(self):
        """ list: Channels settings. """
        return self._channels

    @property
    def counters(self):
        """ dict: Counters information. """

        r = self._transmit(ssp.CMD_COUNTERS_GET)

        return {'stacked': unpack('<I', r[1:1 + 4])[0],
                'stored': unpack('<I', r[5:5 + 4])[0],
                'dispensed': unpack('<I', r[9:9 + 4])[0],
                'transferred': unpack('<I', r[13:13 + 4])[0],
                'rejected': unpack('<I', r[17:17 + 4])[0]}

    def counters_reset(self):
        """ Reset counters. """
        self._transmit(ssp.CMD_COUNTERS_RST)

    def display_enable(self):
        """ Enable display (leds). """
        self._transmit(ssp.CMD_DISP_EN)

    def display_disable(self):
        """ Disable display (leds). """
        self._transmit(ssp.CMD_DISP_DIS)

    def channels_set(self, channels):
        """ Set channels.

            Args:
                channels (tuple, list): Channels to be enabled.
        """

        if not channels:
            channels = ()

        mask = 0
        for channel in channels:
            mask |= (1 << channel)

        self._transmit(ssp.CMD_CH_INHIBITS, pack('<H', mask))

    def enable(self):
        """ Enable. """

        self._transmit(ssp.CMD_ENABLE)

    def disable(self):
        """ Disable. """
        self._transmit(ssp.CMD_DISABLE)

    def poll(self):
        """ Poll for events.

            Returns:
                list: Events occurred since last poll.
        """

        r = self._transmit(ssp.CMD_POLL)

        events = []
        i = 0
        while i < len(r):
            code = r[i]

            if code in (ssp.EVT_READ,
                        ssp.EVT_CREDIT,
                        ssp.EVT_CLEARED_FRONT,
                        ssp.EVT_CLEARED_CASHBOX):
                channel = self._channels[r[i + 1] - 1] if r[i + 1] else None
                i += 2
            else:
                channel = None
                i += 1

            events.append(BillerEvent(code, channel))

        return events
