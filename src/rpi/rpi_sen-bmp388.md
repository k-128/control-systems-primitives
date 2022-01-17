*Circuit*
```cpp
[02] 3.3-5.0V >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL
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
smbus2
```

<br />

*Resources*
- Specs: [01](<https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx>), [02](<http://www.cqrobot.wiki/index.php/BMP388_Barometric_Pressure_Sensor_SKU:_AngelBMP388US>)
