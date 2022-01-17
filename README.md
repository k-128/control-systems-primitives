# Control Systems Primitives
---

<br />

```py
└── rpi
    ├── rpi_ads1115
    ├── rpi_screen-lcd
    ├── rpi_screen-ssd1306
    ├── rpi_sen-bmp388
    ├── rpi_sen-dht
    ├── rpi_sen-ds18b20
    └── rpi_sen-tcs34725
```

<br />

*Resources*
- Diagrams: [circuit-diagram.org](<https://www.circuit-diagram.org/editor/>), [circuito.io](<https://www.circuito.io/>)

<br />

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
```sh
# Server
# -----------------------------------------------------------------------------
sudo apt install openssh-server
ssh localhost  # Should return 'Connection refused' if the server isn't running

# Edit /etc/ssh/sshd_config
Port 9876
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Client
# -----------------------------------------------------------------------------
# Edit /etc/ssh/ssh_config

# Keys:
ssh-keygen
ssh-keygen -t rsa -b 4096 -C "msg"
ssh-keygen -t ed25519 -C "msg"
# ed25519 keys: smaller, faster to generate and verify
# more collision resistant, not quantum resistant (elliptic curve cryptography)
# The public key '.pub' must then be added to the servers ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
# Or, to copy it to a server:
ssh-copy-id <user>@<ip_addr>

# File transfers
scp /path/to/orig <user>@<ip_addr>:/path/to/dest  # A to B
scp <user>@<ip_addr>:/path/to/orig /path/to/dest  # B to A
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
