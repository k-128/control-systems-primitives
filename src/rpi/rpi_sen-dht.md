*Circuit*
```cpp
[02] 5V       >> VCC
[02] 5V       >> 5.1kOhm      >> DATA
[11] GPIO 17  >> DATA
[06] GND      >> GND
```

<br />

*Requirements*
```sh
sudo raspi-config    # Enabled: 1-Wire

# Python pkgs
pigpio  # requires daemon running: `sudo pigpiod`
```

<br />

*Resources*
- Specs: [01](<https://learn.adafruit.com/dht/overview/>)
- [DHT driver](<http://abyz.me.uk/rpi/pigpio/code/DHT.py>)
