from random import choice
from string import ascii_letters, digits
from time import sleep
from typing import Generator
from pytest import mark, fixture
from inoio import InoIO


def generate_random_string(num_strings: int, len_strings: int) -> list[str]:
    alphanumeric = ascii_letters + digits

    result = []

    for _ in range(num_strings):
        result.append("".join(choice(alphanumeric) for _ in range(len_strings)))

    return result


@fixture(scope="module")
def connection(pytestconfig) -> Generator[InoIO, None, None]:
    port = pytestconfig.getoption("port")

    conn = InoIO(port=port)
    conn.connect()

    yield conn
    conn.disconnect()


@mark.parametrize("string", generate_random_string(num_strings=10, len_strings=1))
def test_echo_strings_1(connection: InoIO, string: str) -> None:
    assert connection.write(string) == 1
    assert connection.read() == f"Received message: {string}"


@mark.parametrize("string", generate_random_string(num_strings=10, len_strings=15))
def test_echo_strings_15(connection: InoIO, string: str) -> None:
    assert connection.write(string) == 15
    assert connection.read() == f"Received message: {string}"


@mark.parametrize("string", generate_random_string(num_strings=10, len_strings=50))
def test_echo_strings_50(connection: InoIO, string: str) -> None:
    assert connection.write(string) == 50
    assert connection.read() == f"Received message: {string}"


def test_fifo(connection: InoIO) -> None:
    size_prefix = len("Received message: ")
    extra_newlines = 2

    # ----------
    connection.write("abc")
    sleep(0.05)  # Provide very small delay as serial RX/TX is slow
    assert connection.num_bytes_input_buffer() == 3 + size_prefix + extra_newlines

    # ----------
    connection.write("ab")
    sleep(0.05)
    assert connection.num_bytes_input_buffer() == 5 + (2 * size_prefix) + (
        2 * extra_newlines
    )

    # ----------
    assert connection.read() == "Received message: abc"
    sleep(0.05)
    assert connection.num_bytes_input_buffer() == 2 + size_prefix + extra_newlines

    # ----------
    assert connection.read() == "Received message: ab"
    sleep(0.05)
    assert connection.num_bytes_input_buffer() == 0
