# Executed on every boot, including from deepsleep
#import uos
#import machine
#import webrepl
from esp import osdebug as esp_osdebug
from gc import collect as gc_collect
from network import WLAN, AP_IF, STA_IF

esp_osdebug(None)       # Disabled to avoid Ampy comms errors
gc_collect()
#uos.dupterm(None, 1)    # Disable REPL on UART(0)
#webrepl.start()

WLAN(AP_IF).active(False)   # Disable default Access Point
WLAN(STA_IF).active(False)  # Disable default Station
