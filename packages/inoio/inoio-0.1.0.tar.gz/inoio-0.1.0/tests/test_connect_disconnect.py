from pytest import raises
from inoio import InoIO, errors


def test_invalid_port() -> None:
    conn = InoIO(port=27117)  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_invalid_baudrate() -> None:
    conn = InoIO(baudrate="foobar")  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_invalid_timeout() -> None:
    conn = InoIO(timeout="foobar")  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_invalid_port_init_app() -> None:
    conn = InoIO()
    conn.init_app(port=27117)  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_invalid_baudrate_init_app() -> None:
    conn = InoIO()
    conn.init_app(baudrate="foobar")  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_invalid_timeout_init_app() -> None:
    conn = InoIO()
    conn.init_app(timeout="foobar")  # type: ignore

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    conn.disconnect()
    assert not conn.is_connected
    assert "One or more parameters is of invalid type" in str(excinfo)


def test_connect_disconnect(pytestconfig) -> None:
    port = pytestconfig.getoption("port")
    conn = InoIO(port=port)

    conn.connect()
    conn.write("foobar")

    assert conn.is_connected

    conn.disconnect()
    assert not conn.is_connected

    conn.disconnect()
    assert not conn.is_connected


def test_disconnect_without_connect(pytestconfig) -> None:
    port = pytestconfig.getoption("port")

    conn = InoIO(port=port)
    assert not conn.is_connected

    conn.disconnect()


def test_multiple_connects(pytestconfig) -> None:
    port = pytestconfig.getoption("port")

    conn = InoIO(port=port)
    conn.connect()

    with raises(errors.InoIOConnectionError) as excinfo:
        conn.connect()

    assert f"A connection already exists on {port}" in str(excinfo)
    assert conn.is_connected

    conn.disconnect()


def test_multiple_instances(pytestconfig) -> None:
    port = pytestconfig.getoption("port")

    conn1 = InoIO(port=port)
    conn2 = InoIO(port=port)
    conn1.connect()

    with raises(errors.InoIOConnectionError) as excinfo:
        conn2.connect()

    assert f"Could not connect on {port}" in str(excinfo)

    conn1.disconnect()
    conn2.disconnect()
