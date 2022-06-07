# Control Systems Primitives
---

<br />

```ts
└── src
    ├── arduino
    │   ├── esp8266_ap.ino
    │   ├── esp8266_ap-sen_dht.ino
    │   ├── esp8266_sta.ino
    │   ├── esp8266_sta-mqtt_pub.ino
    │   ├── esp8266_sta-mqtt_pub-sensors.ino
    │   ├── sen_dht.ino
    │   └── sen_ds18b20.ino
    ├── data
    │   ├── db_sensors.py
    │   ├── db_server.py
    │   └── logger.py
    └── rpi
        ├── rpi-ads1115.py
        ├── rpi-gpio.py
        ├── rpi_screen-lcd.py
        ├── rpi_screen-ssd1306.py
        ├── rpi_sen-bmp388.py
        ├── rpi_sen-ctcwtr_cqr.py
        ├── rpi_sen-dht.py
        ├── rpi_sen-ds18b20.py
        ├── rpi_sen-tcs34725.py
        └── rpi_sen-tds_cqr.py
```

<br />

*Resources*
- Diagrams: [circuit-diagram.org](<https://www.circuit-diagram.org/editor/>), [circuito.io](<https://www.circuito.io/>)
- Db: [sqlitebrowser](<https://github.com/sqlitebrowser/sqlitebrowser>)
- Scheduling: [crontab.guru](<https://crontab.guru/>)

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

*WLAN*
```sh
# Setup
# -----------------------------------------------------------------------------
sudo apt install hostapd dnsmasq
sudo systemctl enable --now dnsmasq

sudo cp /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
# Edit: /etc/dnsmasq.conf
interface=wlan0
except-interface=eth0
dhcp-range=192.168.1.96,192.168.1.255,255.255.255.0,24h  # IP rng, DNS mask
dhcp-option=3,192.168.1.1  # Gateway IP address
dhcp-option=6,192.168.1.1  # DNS server address

# If net conf managed by dhcpcd (recent Raspbian)
sudo cp /etc/dhcpcd.conf /etc/dhcpcd.conf.orig
# Edit: /etc/dhcpcd.conf
#denyinterfaces wlan0  # To ignore wireless interface
interface wlan0
static ip_address=192.168.1.20/24
nohook wpa_supplicant  # Will be done with hostapd

# Create: /etc/hostapd/hostapd.conf
interface=wlan0
driver=nl80211             # Driver
channel=6                  # 
hw_mode=g                  # Hardware mode: g=wireless
ssid=ssid                  # Network name
wpa=2                      # WPA Version, 3: both 1 and 2
wpa_passphrase=password    # 
wpa_key_mgmt=WPA-PSK       # 
wpa_pairwise=TKIP          # WPA encryption
rsn_pairwise=CCMP          # WPA2 encryption
country_code=x             # See raspi-config
auth_algs=1                # 1: Only sys auth; 2: Sys & shared key auth
ignore_broadcast_ssid=1    # 1: Hidden Wi-Fi (no ssid broadcast)
macaddr_acl=0              # MAC addr filtering; 0: Accept unless in deny list
# To use:
sudo /usr/sbin/hostapd /etc/hostapd/hostapd.conf
# To set as default, edit: /etc/default/hostapd
DAEMON_CONF="/etc/hostapd/hostapd.conf"

# Exec examples
# -----------------------------------------------------------------------------
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
sudo service dnsmasq start
sudo service --status-all
sudo update-rc.d dnsmasq enable
sudo update-rc.d hostapd enable

# Custom conf
hostapd path/to/hostapd.conf
dnsmasq -C path/to/dnsmasq.conf
```

<br />
