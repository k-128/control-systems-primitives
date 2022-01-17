*Circuit*
```cpp
[02] 5.0V     >> VCC
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
dtparam=i2c_baudrate=115200

# Python pkgs
smbus2
```

<br />

*Resources*
- Specs: [01](<https://www.sparkfun.com/datasheets/LCD/GDM2004D.pdf>)
- [RPi i2c lcd set up and programming](<https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/>)
- [RPi i2c driver](<https://gist.github.com/DenisFromHR/cc863375a6e19dce359d>)
- [Most used baud rates table](<https://lucidar.me/en/serialib/most-used-baud-rates-table/>)
