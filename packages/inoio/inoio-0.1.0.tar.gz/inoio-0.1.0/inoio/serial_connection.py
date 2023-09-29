from time import sleep
import serial
from inoio import errors


class InoIO:

    """Class for interfacing with an Arduino device.

    :param int, optional baudrate: Specify the baud rate.
    :param float, optional timeout: Specify the read and write timeout in seconds.
    :param str, optional port: Specify the device name (i.e. "COM3" on Windows) or path to device
        (i.e. "/dev/ttyS2" on Linux).
    """

    is_connected = False

    def __init__(
        self,
        baudrate: int = 9600,
        port: str = "/dev/ttyS2",
        timeout: float = 5.00,
    ) -> None:
        self.baudrate = baudrate
        self.encoding = "utf-8"
        self.port = port
        self.timeout = timeout

        self.device: serial.Serial

    def init_app(
        self,
        baudrate: int = 9600,
        port: str = "/dev/ttyS2",
        timeout: float = 5.00,
    ) -> None:
        """Override parameters specified via class constructor. This method is useful
        for setting connection parameters if the InoIO class is being used as a Flask extension,
        for example. For more information, see https://flask.palletsprojects.com/en/2.3.x/extensions/

        :param int, optional baudrate: Specify the baud rate.
        :param float, optional timeout: Specify the read and write timeout in seconds.
        :param str, optional port: Specify the device name (i.e. "COM3" on Windows) or path to device
            (i.e. "/dev/ttyS2" on Linux).
        """

        self.baudrate = baudrate
        self.port = port
        self.timeout = timeout

    def connect(self) -> None:
        """Connect to device.

        :raise InoIOConnectionError: If a connection could not be established.
        """

        if self.is_connected:
            raise errors.InoIOConnectionError(
                f"A connection already exists on {self.device.name}"
            )

        try:
            self.device = serial.Serial(
                baudrate=self.baudrate,
                port=self.port,
                timeout=self.timeout,
                write_timeout=self.timeout,
                # Defaults used by Serial.begin()
                # See www.arduino.cc/reference/en/language/functions/communication/serial/begin/
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
        except ValueError as e:
            raise errors.InoIOConnectionError(
                "One or more parameters is of invalid type"
            ) from e
        except serial.serialutil.SerialException as e:
            raise errors.InoIOConnectionError(
                f"Could not connect on {self.port}"
            ) from e

        if not self.device.is_open:
            raise errors.InoIOConnectionError(f"No connection is open on {self.port}")

        # Opening a connection will send a DTR (Data Terminal Ready) signal to device, which will
        # force the device to reset. Give device 2 seconds to reset
        sleep(2)

        self.is_connected = True

    def disconnect(self) -> None:
        """Disconnect from device."""

        if self.is_connected:
            self.device.close()
            self.is_connected = False

    def write(self, message: str) -> int:
        """Send a message to device.

        :param str, message: Specify the message to be sent.
        :returns: The number of bytes written.
        :rtype: int
        :raises InoIOTransmissionError: If message could not be sent.
        """

        if not self.is_connected:
            raise errors.InoIOTransmissionError(
                "Cannot send message. No connection is open"
            )

        if not isinstance(message, str):
            raise errors.InoIOTransmissionError(
                "Cannot send message. Message is not of 'str' type"
            )

        message_encoded = message.encode(encoding=self.encoding)

        try:
            bytes_written = self.device.write(message_encoded)
        except Exception as e:
            raise errors.InoIOTransmissionError("Failed to write to device") from e

        try:
            self.device.flush()
        except Exception as e:
            raise errors.InoIOTransmissionError("Failed to write to device") from e

        return bytes_written

    def read(self) -> str:
        """Read a message from device.

        :returns: The message that was read from device.
        :rtype: str
        :raises InoIOTransmissionError: If message could not be read.
        """

        if not self.is_connected:
            raise errors.InoIOTransmissionError(
                "Cannot read from device. No connection is open"
            )

        message_received = False

        while not message_received:
            while self.device.in_waiting < 1:
                pass

            bytes_from_dev = self.device.read_until()  # Reads until \n by default
            message_received = True

        try:
            message = bytes_from_dev.decode(self.encoding).strip()
        except UnicodeDecodeError as e:
            raise errors.InoIOTransmissionError("Failed to decode data") from e

        return message
