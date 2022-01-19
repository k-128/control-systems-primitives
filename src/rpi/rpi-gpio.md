*Circuit*
```cpp
[02] 5.0V     >> RELAY_VCC
[06] GND      >> RELAY_GND
[29] GPIO 05  >> RELAY_IN1
[31] GPIO 06  >> RELAY_IN2
[12] GPIO 18  >> BUTTON       >> GND
[16] GPIO 23  >> LED_IN1      >> RESISTOR     >> GND
[18] GPIO 24  >> LED_IN2      >> RESISTOR     >> GND
```

<br />

*Requirements*
```sh
# Python pkgs
RPi.GPIO
gpiozero
```

<br />

*Resources*
- [RPi.GPIO docs](<https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/>)
- gpiozero: [git](<https://github.com/gpiozero/gpiozero>), [docs](<https://gpiozero.readthedocs.io/en/stable/>)
