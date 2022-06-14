### MicroPython
---

<br />

*Setup*
- Dl firmware to flash, ex: [micropython.org/download/esp8266](<https://micropython.org/download/esp8266/>) (contains [umqtt](<https://github.com/micropython/micropython-lib/tree/master/micropython>))

```sh
python -m pip install esptool

# Plug the devkit usb and get <serial_port>:
ls /dev/tty*
# nix ex: dev/ttyUSB0
# win ex: COM4

# Flash firmware to the devkit:
sudo chmod 666 <serial_port>
esptool.py --port <serial_port> erase_flash  # Erase old firmware
esptool.py --port <serial_port> write_flash --flash_size=detect -fm dio 0 <micropyhton-firmware>.bin
```

- Board file management with ampy ([git: scientifichackers/ampy](<https://github.com/scientifichackers/ampy>))

```sh
python -m pip install adafruit-ampy

# Disable DEBUG mode (causes issues with Ampy)
# - Connect to the board's MicroPython REPL, using putty or picocom: -b 115200
>>> import esp
>>> esp.osdebug(None)
# - Close connection

# Examples:
ampy --port COM4 --baud 115200 ls
ampy --port COM4 --baud 115200 put src/to_board/ .
ampy --port COM4 --baud 115200 get . src/from_board/
ampy --port COM4 --baud 115200 rm <file/path>
```

<br />
