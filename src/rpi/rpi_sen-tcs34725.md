*Circuit*
```cpp
[02] 3.3-5.0V >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL
[11] GPIO 17  >> INT
[12] GPIO 18  >> LED
```

<br />

*Requirements*
```py
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi

# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=921600

# Python pkgs
RPi.GPIO
adafruit-circuitpython-tcs34725
```

<br />

*Resources*
- Specs: [01](<https://pdf1.alldatasheet.com/datasheet-pdf/view/894928/AMSCO/TCS34725.html>), [02](<http://www.cqrobot.wiki/index.php/TCS34725_Color_Sensor>)
- Adafruit CircuitPython TCS34725: [git](<https://github.com/adafruit/Adafruit_CircuitPython_TCS34725>), [docs: implementation notes](<https://circuitpython.readthedocs.io/projects/tcs34725/en/latest/api.html#implementation-notes>)
- [RPi.GPIO docs](<https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/>)
- [Most used baud rates table](<https://lucidar.me/en/serialib/most-used-baud-rates-table/>)