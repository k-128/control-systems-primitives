### RPi
---

<br />

*Resources*
- [Website](<https://www.raspberrypi.org/>), [wiki](<https://en.wikipedia.org/wiki/Raspberry_Pi>)
- Pin mappings: [Microsoft](<https://docs.microsoft.com/en-us/windows/iot-core/learn-about-hardware/pinmappings/pinmappingsrpi>), [pinout.xyz](<https://pinout.xyz/>)
- Diagrams: [Fritzing](<https://github.com/fritzing/fritzing-app>), [Fritzing svg](<https://github.com/fritzing/fritzing-parts/tree/master/svg/core/breadboard>), [RPi components](<https://github.com/raspberrypilearning/components>)
- Libs: [RPi.GPIO](<https://pypi.org/project/RPi.GPIO/>), [gpiozero](<https://github.com/gpiozero/gpiozero>), [pigpio](<https://github.com/joan2937/pigpio>), [i2c-tools](<https://packages.debian.org/buster/utils/i2c-tools>), [smbus2](<https://github.com/kplindegaard/smbus2>), [picamera](<https://github.com/picamera>), [MQTT IO](<https://github.com/flyte/mqtt-io>)
  - [adafruit-circuitpython](<https://github.com/adafruit/circuitpython>): [ads1x15](<https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15>), [ssd1306](<https://github.com/adafruit/Adafruit_CircuitPython_SSD1306>), [tcs34725](<https://github.com/adafruit/Adafruit_CircuitPython_TCS34725>)

<br />

*Setup*
- Imagers: [RPi](<https://www.raspberrypi.org/software/>), [Balena Etcher](<https://www.balena.io/etcher/>)
- OS: [Raspbian](<https://www.raspbian.org/>), [Kali](<https://www.kali.org/get-kali/#kali-arm>)

```sh
sudo raspi-config

# User mgmt
# -----------------------------------------------------------------------------
sudo passwd root     # Enable root account
sudo passwd -l root  # Disable root account
sudo passwd -d root  # Disable root account
sudo passwd <user>   # Change password
cat /etc/passwd      # List users
useradd <uid>        # Add user
userdel -r <uid>     # Del user, -r: rm home directory

# Rename user, as root:
usermod -l <new_user> <user>
usermod -m -d /home/<new_user> <new_user>
visudo /etc/sudoers.d/<user>
# <user> ALL=(ALL) NOPASSWD: ALL

# Autologin
sudo nano /etc/lightdm/lightdm.conf
#autologin-user=<user>

# Network
# -----------------------------------------------------------------------------
hostname                 # Display hostname
sudo nano /etc/hostname  # Edit
sudo nano /etc/hosts     # ..., alternatively, raspi-config can be used
ip a                     # RPI ip
ip r | grep default      # 
nmap -sn 192.168.1.*     # Ex nmap from a network accessible device
```

<br />

*SSH*
- See [networking/src/set_ssh_server.sh](../networking/src/set_ssh_server.sh)
- Usage:

```sh
# File transfers
scp -P <port> /path/to/orig <user>@<ip/host>:/path/to/dest  # A to B
scp -P <port> <user>@<ip/host>:/path/to/orig /path/to/dest  # B to A
rsync -rvz --no-perms -e "ssh -p 80" --filter=":- .gitignore" --exclude="venv/" path/to/orig <user>@<ip_addr>:path/to/dest/
# -r: recursive
# -v: verbose
# -z: zip
# -a: archive mode == -rlptgoD, for backups

# To avoid reentering passphrases
eval $(ssh-agent -s)
ssh-add

# Debug
tail /var/log/auth.log
```

<br />

*RTC*
```sh
sudo apt-get install i2c-tools

# Edit /boot/config.txt:
dtparam=i2c_arm=on        # Enable i2c, or: sudo raspi-config
dtoverlay=i2c-rtc,ds3231  # Enable ds3231 module

# Edit /lib/udev/hwclock-set, comment out RPi/RTC auto updates:
#if [ -e /run/systemd/system ] ; then 
#   exit 0
#fi
#if [ yes = "$BADYEAR" ]; then
#    /sbin/hwclock --rtc=$dev --systz --badyear
#    /sbin/hwclock --rtc=$dev --hctosys --badyear
#else
#    /sbin/hwclock --rtc=$dev --systz
#    /sbin/hwclock --rtc=$dev --hctosys
#fi

# Reboot for changes to take effect
sudo reboot
sudo i2cdetect -y 1  # 0 for older RPi
# If enabled: #68 should show up as #UU

# To avoid RTC corruption
sudo systemctl stop ntp.service
sudo systemctl disable ntp.service
sudo systemctl stop fake-hwclock.service
sudo systemctl disable fake-hwclock.service
sudo systemctl stop systemd-timesyncd.service
sudo systemctl disable systemd-timesyncd.service

# Usage
sudo hwclock -r  # Read RTC time
sudo hwclock -w  # Copy sys time to RTC
sudo hwclock -s  # Copy RTC time to sys
sudo hwclock --set --date="2022-01-01 12:00:00"  # Set RTC time
sudo date -s "01 JAN 2022 12:00:00"              # Set sys time

# Debug
timedatectl status
dmesg | grep rtc
cat /var/log/syslog | grep "Time has been changed"
```

<br />

### src/
---

*Resources*
- [RPi.GPIO docs](<https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/>)
- [Most used baud rates table](<https://lucidar.me/en/serialib/most-used-baud-rates-table/>)

<br />

*rpi_screen-lcd*
- Specs: [01](<https://www.sparkfun.com/datasheets/LCD/GDM2004D.pdf>)
- [RPi i2c lcd set up and programming](<https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/>)
- [RPi i2c driver](<https://gist.github.com/DenisFromHR/cc863375a6e19dce359d>)

```sh
[02] 5.0V     >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL

# RPi
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi
# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=115200

# Python pkgs
smbus2
```

<br />

*rpi_screen-ssd1306*
- Specs: [01](<https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf>)
- [Wiring](<https://learn.adafruit.com/monochrome-oled-breakouts/python-wiring>)
- [Examples](<https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/tree/main/examples>)
- [Pillow docs](<https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html>)

```sh
[02] 3.3V     >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL

# RPi
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

*rpi_sen-bmp388*
- Specs: [01](<https://learn.adafruit.com/adafruit-bmp388-bmp390-bmp3xx>), [02](<http://www.cqrobot.wiki/index.php/BMP388_Barometric_Pressure_Sensor_SKU:_AngelBMP388US>)

```sh
[02] 3.3-5.0V >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL

# RPi
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi
# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=921600

# Python pkgs
smbus2
```

<br />

*rpi_sen-ctcwtr_cqr*
- Specs: [01](<http://www.cqrobot.wiki/index.php/Contact_Water/Liquid_Level_Sensor_SKU:_CQRSENYW002>)

```sh
[04] 5V       >> VCC
[06] GND      >> GND
[18] GPIO 18  >> DATA

# Python pkgs
RPi.GPIO
```

<br />

*rpi_sen-dht*
- Specs: [01](<https://learn.adafruit.com/dht/overview/>)
- [DHT driver](<http://abyz.me.uk/rpi/pigpio/code/DHT.py>)

```sh
[02] 5V       >> VCC
[02] 5V       >> 5.1kOhm      >> DATA
[11] GPIO 17  >> DATA
[06] GND      >> GND

# RPi
sudo raspi-config    # Enabled: 1-Wire

# Python pkgs
pigpio  # requires daemon running: `sudo pigpiod`
```

<br />

*rpi_sen-ds18b20*
- Specs: [01](<https://cdn-shop.adafruit.com/datasheets/DS18B20.pdf>), [02](<https://www.adafruit.com/product/381>)

```sh
[02] 5V       >> VCC
[02] 5V       >> 5.1kOhm      >> DATA
[07] GPIO 4   >> DATA
[06] GND      >> GND

# RPi
sudo raspi-config    # Enabled: 1-Wire
# pgpiod requires read perms, edit /opt/pigpio/access:
/sys/bus/w1/devices/* r

# Python pkgs
pigpio  # requires daemon running: `sudo pigpiod`
```

<br />

*rpi_sen-tcs34725*
- Specs: [01](<https://pdf1.alldatasheet.com/datasheet-pdf/view/894928/AMSCO/TCS34725.html>), [02](<http://www.cqrobot.wiki/index.php/TCS34725_Color_Sensor>)
- Adafruit CircuitPython TCS34725: [git](<https://github.com/adafruit/Adafruit_CircuitPython_TCS34725>), [docs: implementation notes](<https://circuitpython.readthedocs.io/projects/tcs34725/en/latest/api.html#implementation-notes>)

```sh
[02] 3.3-5.0V >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL
[11] GPIO 17  >> INT
[12] GPIO 18  >> LED

# RPi
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

*rpi_sen-tds_cqr*
- Specs: [01](<http://www.cqrobot.wiki/index.php/TDS_(Total_Dissolved_Solids)_Meter_Sensor_SKU:_CQRSENTDS01>)
- ADS1x15:
  - Specs: [01](<https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython/>), [02](<http://www.cqrobot.wiki/index.php/ADS1115_16-Bit_ADC_Module_SKU:_CQRADS1115>)
  - Adafruit CircuitPython ADS1x15: [git](<https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/>), [docs](<https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/>)

```sh
[02] 3.3-5.0V >> VCC          >> TDS_VCC
[06] GND      >> GND          >> TDS_GND
[03] GPIO 2   >> ADS_SDA
[05] GPIO 3   >> ADS_SCL
              >> ADS_AX       >> TDS_DATA

# RPi
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi
# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=921600

# Python pkgs
adafruit-circuitpython-ads1x15
```

<br />

*rpi-ads1x15*
- Specs: [01](<https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython/>), [02](<http://www.cqrobot.wiki/index.php/ADS1115_16-Bit_ADC_Module_SKU:_CQRADS1115>)
- Adafruit CircuitPython ADS1x15: [git](<https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15/>), [docs](<https://circuitpython.readthedocs.io/projects/ads1x15/en/latest/>)

```sh
[02] 3.3-5.0V >> VCC
[06] GND      >> GND
[03] GPIO 2   >> SDA
[05] GPIO 3   >> SCL

# RPi
sudo raspi-config    # Enabled: I2C
sudo apt install i2c-tools
sudo i2cdetect -y 1  # 0 for older RPi
# To set i²c speed, edit /boot/config.txt:
dtparam=i2c_baudrate=921600

# Python pkgs
adafruit-circuitpython-ads1x15
```

<br />

*rpi-camera*

```sh
# RPi
sudo raspi-config    # Enabled: Camera

# Python pkgs
apscheduler  # If no time server: RTC (Real Time Clock) or GPS advised
picamera
```

<br />

*rpi-gpio*
- [RPi.GPIO docs](<https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/>)
- gpiozero: [git](<https://github.com/gpiozero/gpiozero>), [docs](<https://gpiozero.readthedocs.io/en/stable/>)

```sh
[02] 5.0V     >> RELAY_VCC
[06] GND      >> RELAY_GND
[29] GPIO 05  >> RELAY_IN1
[31] GPIO 06  >> RELAY_IN2
[12] GPIO 18  >> BUTTON       >> GND
[16] GPIO 23  >> LED_IN1      >> RESISTOR     >> GND
[18] GPIO 24  >> LED_IN2      >> RESISTOR     >> GND

# Python pkgs
RPi.GPIO
gpiozero
```

<br />
