import json
from time import sleep

from machine import idle
from network import WLAN, AP_IF, STA_IF
try:
    import usocket as socket
except:
    import socket


AP_SSID         = ""
AP_PASSWORD     = ""
AP_IP_ADDRESS   = "192.168.1.128"
AP_HIDDEN       = False
AUTH_MODES      = ["0", "OPEN", "WEP", "WPA-PSK", "WPA2-PSK", "WPA/WPA2-PSK"]


def set_interface_state(iface: WLAN, state: bool) -> None:
    iface.active(state)


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
    ap.config(
        essid=ssid,               # (str)   AP Name
        password=password,        # (str)   AP Password
        hidden=hidden,            # (bool)  SSID hidden
        # dhcp_hostname=hostname, # (str)   DHCP hostname
        # mac                     # (bytes) MAC address
        # channel                 # (int)   WiFi Channel
        # authmode                # (int)   Auth mode
        # reconnects              # (int)   Nb of reconnect attempts, -1: inf.
        # txpower                 # (float) Maximum transmit power in dBm
    )
    while not ap.active():
        idle()
    print(f"Access Point created. Config: {ap.ifconfig()}")


def connect_to_access_point(
    ssid: str       = AP_SSID,
    password: str   = AP_PASSWORD
) -> None:
    print(f"Connecting to ssid[{ssid}]...")
    sta = WLAN(STA_IF)
    sta.active(True)
    if not sta.isconnected():
        sta.connect(ssid, password)
        while not sta.isconnected():
            idle()
    print(f"Connected. Network config: {sta.ifconfig()}")


def scan_wlan(verbose: bool=False) -> list[tuple[str, str, str, str, int, int]]:
    '''Get list of tuple: [(SSID, BSSID, Channel, RSSI, Authmode, Hidden), ]'''
    print(f"Scanning WiFi...")
    sta = WLAN(STA_IF)
    sta.active(True)
    nets = sta.scan()
    if verbose:
        for n in nets:
            print(
                f"- SSID: {n[0]}\tBSSID: {n[1]}\tChannel: {n[2]}\t",
                f"RSSI: {n[3]}\tAuthmode: {AUTH_MODES[n[4]]}\tHidden: {n[5]}"
            )
    return nets


def run_http_server() -> None:
    addr_info   = socket.getaddrinfo("0.0.0.0", 80)
    addr        = addr_info[0][-1]
    skt         = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    skt.bind(addr)
    skt.listen(5)  # Queue up as many as 5 connect requests before refusing
    print(f"Listening..., bind address info: {addr_info}")

    while True:
        conn, addr = skt.accept()
        print(f"Recv. request from: {addr}: ")

        # MicroPython sockets support stream interfaces directly
        stream = conn  # else: conn.makefile("rwb")
        while True:
            q = stream.readline()
            if q == b"" or q == b"\r\n":
                break
        stream.write(json.dumps({"hello": "world"}))
        conn.close()


if __name__ == "__main__":
    # set_interface_state(AP_IF, True)
    # create_access_point()
    # connect_to_access_point()
    # run_http_server_socket()
    scan_wlan(True)
    # run_http_server()
