*Circuit*
```cpp
[02] 3.3V     >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL
```

<br />

*Requirements*
```sh
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi

# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=921600

# Python pkgs
pillow
adafruit-circuitpython-ssd1306
```

<br />

*Resources*
- [Wiring](<https://learn.adafruit.com/monochrome-oled-breakouts/python-wiring>)
- [Examples](<https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/tree/main/examples>)
- [Pillow docs](<https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html>)
- [Most used baud rates table](<https://lucidar.me/en/serialib/most-used-baud-rates-table/>)
