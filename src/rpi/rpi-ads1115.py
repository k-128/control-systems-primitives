from time import sleep

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)


def test_channels() -> None:
    try:
        channels = {
            # Single-ended inputs
            "Sgl-0": AnalogIn(ads, ADS.P0),
            "Sgl-1": AnalogIn(ads, ADS.P1),
            "Sgl-2": AnalogIn(ads, ADS.P2),
            "Sgl-3": AnalogIn(ads, ADS.P3),
            # Differential inputs
            "Diff-01": AnalogIn(ads, ADS.P0, ADS.P1)
        }
        while True:
            print("\nChannel\tVoltage\tValue")
            print("-------\t-------\t-----")
            for k, v in channels.items():
                print(f"{k}\t{v.voltage:>5.3f}\t{v.value:>5} V")

            sleep(1)
    except Exception as e:
        print(f"{e}")


def test_potentiometer(pin: int=ADS.P0, max_voltage: float=4.096) -> None:
    try:
        c = AnalogIn(ads, pin)
        while True:
            pct = c.voltage / max_voltage * 100
            pct = 0 if pct <= 0 else pct
            print(f"Voltage: {c.voltage:>5.3f}\tPercent: {pct:.2f}")
            sleep(1)
    except Exception as e:
        print(f"{e}")


if __name__ == "__main__":
    # test_channels()
    test_potentiometer()
