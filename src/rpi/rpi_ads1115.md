*Circuit*
```cpp
[02] 3.3-5.0V >> VCC
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
adafruit-circuitpython-ads1x15
```

<br />

*Resources*
- Specs: [01](<https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython/>), [02](<http://www.cqrobot.wiki/index.php/ADS1115_16-Bit_ADC_Module_SKU:_CQRADS1115>)
- Adafruit CircuitPython ADS1x15: [git](<https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/>), [docs](<https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/>)
- [Most used baud rates table](<https://lucidar.me/en/serialib/most-used-baud-rates-table/>)
