from time import sleep

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 2/3  # +-6.144 V - CQR-TDS
tds_in = AnalogIn(ads, ADS.P1)


def read_tds_cqr(temperature: float = 25.0) -> float:
    """Read Total Dissolved Solids CQR sensor

    Params:
    - temperature: float = 25.0, celsius
    """
    tds = 0.0
    try:
        compens_coef = 0.02 * (temperature - 25.0) + 1
        v = tds_in.voltage / compens_coef
        tds = (133.42 * pow(v, 3) - 255.86 * pow(v, 2) + 857.39 * v) / 2
    except Exception as e:
        print(f"{e}")
    return round(tds, 2)


if __name__ == "__main__":
    while True:
        print(f"TDS: {read_tds_cqr():.2f} ppm")
        sleep(1)
