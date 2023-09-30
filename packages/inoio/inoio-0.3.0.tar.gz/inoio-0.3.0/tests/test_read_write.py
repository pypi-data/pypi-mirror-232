from typing import Generator
from pytest import raises, fixture, mark
from inoio import InoIO, errors


@fixture(scope="module")
def connection(pytestconfig) -> Generator[InoIO, None, None]:
    port = pytestconfig.getoption("port")
    conn = InoIO(port=port)

    yield conn
    conn.disconnect()


def test_write_to_disconnected_device(connection: InoIO) -> None:
    with raises(errors.InoIOTransmissionError) as excinfo:
        connection.write("foobar")

    assert "Cannot send message. No connection is open" in str(excinfo)


def test_read_from_disconnected_device(connection: InoIO) -> None:
    with raises(errors.InoIOTransmissionError) as excinfo:
        connection.read()

    assert "Cannot read from device. No connection is open" in str(excinfo)


def test_connect_disconnect_write(connection: InoIO) -> None:
    connection.connect()
    connection.disconnect()

    with raises(errors.InoIOTransmissionError) as excinfo:
        connection.write("foobar")

    assert "Cannot send message. No connection is open" in str(excinfo)


def test_connect_disconnect_read(connection: InoIO) -> None:
    connection.connect()
    connection.disconnect()

    with raises(errors.InoIOTransmissionError) as excinfo:
        connection.read()

    assert "Cannot read from device. No connection is open" in str(excinfo)


@mark.skip(reason="Read timeout seems to not work on pySerial end")
def test_read_timeout(connection: InoIO) -> None:
    connection.connect()
    connection.read()
