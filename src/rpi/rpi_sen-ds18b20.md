*Circuit*
```cpp
[02] 5V       >> VCC
[02] 5V       >> 5.1kOhm      >> DATA
[07] GPIO 4   >> DATA
[06] GND      >> GND
```

<br />

*Requirements*
```sh
sudo raspi-config    # Enabled: 1-Wire

# Python pkgs
pigpio  # requires daemon running: `sudo pigpiod`

# pgpiod requires read perms, edit /opt/pigpio/access
/sys/bus/w1/devices/* r
```

<br />

*Resources*
- Specs: [01](<https://cdn-shop.adafruit.com/datasheets/DS18B20.pdf>), [02](<https://www.adafruit.com/product/381>)
