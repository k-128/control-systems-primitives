import json
from time import sleep

import dht
from machine import Pin, idle, unique_id
from network import WLAN, STA_IF, AP_IF
from ubinascii import hexlify
from umqtt.simple import MQTTClient


AP_SSID             = ""
AP_PASSWORD         = ""
MQTT_IP_ADDRESS     = ""
MQTT_PORT           = 1883
MQTT_USER           = ""
MQTT_PASSWORD       = ""
SENSOR              = dht.DHT22(Pin(4))  # GPIO
SENSOR_ERROR_VALUE  = -273.15


def connect_to_access_point(
    ssid: str       = AP_SSID,
    password: str   = AP_PASSWORD
) -> None:
    print(f"Connecting to ssid[{ssid}]...")
    sta = WLAN(STA_IF)
    sta.active(True)
    sta.connect(ssid, password)
    while not sta.isconnected():
        idle()
    print(f"Connected. Network config: {sta.ifconfig()}")


def publish_sensor_data(
    sensor: dht.DHTBase = SENSOR,
    ip_address: str     = MQTT_IP_ADDRESS,
    port: int           = MQTT_PORT,
    user: str           = MQTT_USER,
    password: str       = MQTT_PASSWORD,
    keepalive: int      = 0,
    ssl: bool           = False,
    ssl_params: any     = {}
) -> None:
    client_id = hexlify(unique_id())
    c = MQTTClient(
        client_id=client_id,
        server=ip_address,
        port=port,
        user=user,
        password=password,
        keepalive=keepalive,
        ssl=ssl,
        ssl_params=ssl_params,
    )
    print(f"Connecting MQTT Client: {client_id}\t{ip_address}...")

    try:
        c.connect(clean_session=False)
    except Exception as e:
        print(f"Error connection: {e}")

    while True:
        data = {"temp": SENSOR_ERROR_VALUE, "rh": SENSOR_ERROR_VALUE}
        try:
            sensor.measure()
            data["temp"] = sensor.temperature()
            data["rh"]   = sensor.humidity()
        except:
            pass

        print(f"Publishing sensor data: {data}")
        c.publish(b"sen/dht", json.dumps(data, ensure_ascii=False).encode())
        sleep(1)
    # c.disconnect()


if __name__ == "__main__":
    WLAN(AP_IF).active(False)
    connect_to_access_point()
    publish_sensor_data()
