# InoIO
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A small library for RX/TX with Arduino devices.

## Table of Contents
- [Installation](#installation)
- [Example](#example)

## Installation
To install the library, simply run:
```
pip install inoio
```

## Example
The following snippet demonstrates how to use the library:
```python
import sys
from inoio import InoIO, errors


def main() -> None:
    conn = InoIO(port="/dev/ttyS2", baudrate=9600)

    try:
        conn.connect()
    except errors.InoIOConnectionError:
        sys.exit("Failed to connect")

    conn.write("A foo that bars")
    print(conn.read())

    conn.disconnect()


if __name__ == "__main__":
    main()
```
Running this small program would return:
```
Received message: A foo that bars
```
Assuming the following code is uploaded to the device and the device is running:
```C++
void setup()
{
    unsigned int baudrate = 9600;
    ::Serial.begin(baudrate);

    unsigned int timeout_msec = 10;
    ::Serial.setTimeout(timeout_msec);
}

void loop()
{
    while (::Serial.available() > 0)
    {
        ::String message = ::Serial.readString();
        message.trim();

        ::Serial.println("Received message: " + message);
        ::Serial.flush();
    }
}
```
