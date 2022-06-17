from dataclasses import dataclass
from time import sleep, time
from typing import Tuple

import pigpio


@dataclass
class Model:
    auto: int  = 0
    DHT11: int = 1
    DHTXX: int = 2


@dataclass
class Status:
    ok: int           = 0  # Good reading
    bad_checksum: int = 1  # Recv data failed checksum check
    bad_data: int     = 2  # Recv data had one or more invalid values
    timeout: int      = 3  # No response from sensor


@dataclass
class Reading:
    timestamp: float         = time()
    status: Status           = Status.timeout
    temperature: float       = 0.0  # Celsius
    relative_humidity: float = 0.0  # %

    def __repr__(self) -> str:
        return f"{self.timestamp:.2f} [{self.status}] " \
            f"{self.temperature}°C, Rh: {self.relative_humidity} %"


class DHT:
    """
    Utility class to read DHTXX temperature/humidity sensors

    Params
    - pi: pigpio.pi
    - gpio: int
    - model: int = Model.auto

    ```md
    Ranges
    +-----------------------+------------+------------+
    |                 Model |      DHT11 |      DHTXX |
    +-----------------------+------------+------------+
    |       Temperature (C) |    0 to 50 | -40 to 125 |
    | Relative humidity (%) |   20 to 80 |   0 to 100 |
    +-----------------------+------------+------------+

    Data
    +--------+----------+----------+----------+----------+----------+
    |  Bytes |        0 |        1 |        2 |        3 |        4 |
    |--------+----------+----------+----------+----------+----------+
    |  DHT11 | checksum |        0 | Temp int |        0 |   Rh int |
    |  DHTXX | checksum | Temp dec | Temp int |   Rh dec |   Rh int |
    +--------+----------+----------+----------+----------+----------+
    ```
    """

    def __init__(
        self,
        pi: pigpio.pi,
        gpio: int,
        model: int = Model.auto
    ) -> None:
        self._pi       = pi
        self._gpio     = gpio
        self._model    = model

        # Data processing
        self._is_processing = False
        self._bits          = 0
        self._data          = 0
        self._reading       = Reading()
        self._has_new_data_been_processed = False

        # pigpio (tick: microseconds since system boot)
        pi.set_mode(gpio, pigpio.INPUT)
        self._prev_tick = pi.get_current_tick() - 10_000
        self._callback_id = pi.callback(
            gpio,
            pigpio.RISING_EDGE,
            self._on_rising_edge
        )

    def __repr__(self) -> str:
        return f"DHT.{self._model} GPIO[{self._gpio}]"

    def __del__(self) -> None:
        pass

    @staticmethod
    def get_DHT11_data(b1: int, b2: int, b3: int, b4: int) -> Tuple[int, ...]:
        t = b2
        h = b4
        is_valid = False
        if (b1 == 0) and (b3 == 0) and (t <= 60) and (h >= 10) and (h <= 90):
           is_valid = True
        return (is_valid, t, h)

    @staticmethod
    def get_DHTXX_data(b1: int, b2: int, b3: int, b4: int) -> Tuple[int, ...]:
        div = -10.0 if b2 & 128 else 10.0
        t = float(((b2 & 127) << 8) + b1) / div
        h = float((b4 << 8) + b3) / 10.0
        is_valid = False
        if (h <= 110.0) and (t >= -50.0) and (t <= 135.0):
            is_valid = True
        return (is_valid, t, h)

    def _decode_dhtxx(self):
        b0 =  self._data        & 0xFF
        b1 = (self._data >>  8) & 0xFF
        b2 = (self._data >> 16) & 0xFF
        b3 = (self._data >> 24) & 0xFF
        b4 = (self._data >> 32) & 0xFF
        chksum = (b1 + b2 + b3 + b4) & 0xFF

        if chksum == b0:
            is_valid = False

            if self._model == Model.DHTXX:
                is_valid, t, h = self.get_DHTXX_data(b1, b2, b3, b4)
            elif self._model == Model.DHT11:
                is_valid, t, h = self.get_DHT11_data(b1, b2, b3, b4)
            elif self._model == Model.auto:
                is_valid, t, h = self.get_DHTXX_data(b1, b2, b3, b4)
                if not is_valid:
                    is_valid, t, h = self.get_DHT11_data(b1, b2, b3, b4)

            if is_valid:
                self._reading.temperature       = t
                self._reading.relative_humidity = h
                self._reading.status            = Status.ok
            else:
                self._reading.status = Status.bad_data
        else:
            self._reading.status = Status.bad_checksum
        self._reading.timestamp = time()
        self._has_new_data_been_processed = True

    def _on_rising_edge(self, gpio, level, tick):
        """pigpio callback"""
        # Get delta between the current and previous ticks
        t_since_last_cb = pigpio.tickDiff(self._prev_tick, tick)
        self._prev_tick = tick

        if t_since_last_cb > 10_000:
            self._is_processing = True
            self._bits = -2
            self._data = 0
        elif self._is_processing:
            self._bits += 1
            if self._bits >= 1:
                self._data <<= 1
                if (t_since_last_cb >= 60) and (t_since_last_cb <= 150):
                    if t_since_last_cb > 100:
                        self._data += 1
                else:
                    self._is_processing = False
            if self._is_processing:
                if self._bits == 40:
                    self._decode_dhtxx()
                    self._is_processing = False

    def stop(self) -> None:
        """Remove _on_rising_edge callback from pigpio notification thread"""
        if self._callback_id is not None:
            self._callback_id.cancel()
            self._callback_id = None

    def read(self) -> Reading:
        self._reading.status = Status.timeout
        self._has_new_data_been_processed = False

        # Trigger reading
        self._pi.write(self._gpio, 0)
        if self._model != Model.DHTXX:
            sleep(0.018)
        else:
            sleep(0.001)
        self._pi.set_mode(self._gpio, pigpio.INPUT)

        # Wait for reading
        for _ in range(5):
            sleep(0.05)
            if self._has_new_data_been_processed:
                break
        return self._reading


if __name__ == "__main__":
    from datetime import datetime

    pi = pigpio.pi()
    if not pi.connected:
        exit()

    sen = DHT(pi, 17)
    try:
        while True:
            r = sen.read()
            print(f"{datetime.now()} - {r.__repr__()}")
            sleep(1)
    finally:
        sen.stop()
        pi.stop()
        print("pigpio cleaned up")
