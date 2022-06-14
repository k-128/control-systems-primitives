from time import sleep

import dht
from machine import Pin


SENSOR              = dht.DHT22(Pin(4))  # GPIO
SENSOR_ERROR_VALUE  = -273.15


def get_dht_data(sen: dht.DHTBase = SENSOR) -> tuple[float, float]:
    '''Get dht data tuple: (temperature: °C, Relative humidity: %)'''
    try:
        sen.measure()
        return (sen.temperature(), sen.humidity())
    except:
        return (SENSOR_ERROR_VALUE, SENSOR_ERROR_VALUE)


if __name__ == "__main__":
    while True:
        temp, rh = get_dht_data()
        print(f"Temperature: {temp} °C\tRelative humidity: {rh} %")
        sleep(1)
