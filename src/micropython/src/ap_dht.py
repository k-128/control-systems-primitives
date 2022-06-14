import json
from time import sleep

import dht
from machine import Pin
from network import WLAN, AP_IF
try:
    import usocket as socket
except:
    import socket


AP_SSID             = ""
AP_PASSWORD         = ""
AP_IP_ADDRESS       = "192.168.1.128"
AP_HIDDEN           = False
SENSOR              = dht.DHT22(Pin(4))  # GPIO
SENSOR_ERROR_VALUE  = -273.15


def create_access_point(
    ssid: str       = AP_SSID,
    password: str   = AP_PASSWORD,
    ip_address: str = AP_IP_ADDRESS,
    hidden: bool    = AP_HIDDEN
) -> None:
    print(f"Creating Access Point: ssid[{ssid}]...")
    ap = WLAN(AP_IF)
    ap.active(True)
    c = ap.ifconfig()  # tuple: (IP address, Subnet mask, Gateway, DNS server)
    ap.ifconfig((ip_address, c[1], c[2], c[3]))
    ap.config(essid=ssid, password=password, hidden=hidden)
    while not ap.active():
        sleep(1)
        print(f"Creating Access Point: ssid[{ssid}]...")
    print(f"Access Point created. Config: {ap.ifconfig()}")


def run_http_server(sensor: dht.DHTBase = SENSOR) -> None:
    addr_info   = socket.getaddrinfo("0.0.0.0", 80)
    addr        = addr_info[0][-1]
    skt         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.bind(addr)
    skt.listen(5)
    print(f"Listening..., bind address info: {addr_info}")

    while True:
        conn, addr = skt.accept()
        data = {"temp": SENSOR_ERROR_VALUE, "rh": SENSOR_ERROR_VALUE}
        try:
            sensor.measure()
            data["temp"] = sensor.temperature()
            data["rh"]   = sensor.humidity()
        except:
            pass

        conn.recv(1024)
        conn.write(json.dumps(data))
        conn.close()


if __name__ == "__main__":
    create_access_point()
    run_http_server()
