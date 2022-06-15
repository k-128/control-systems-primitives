#!/usr/bin/env bash
#
# Set a Wireless Access Point routing to eth0 using IP masquerading

set -o errexit   # Exit if non-zero exit code, ...
set -o nounset   # Exit if unset variables, ...
set -o pipefail  # Exit if non-zero exit code, ...

readonly SCRIPT_NAME="${0##*/}"
readonly PATH_DIR=$(dirname $(readlink -f $0))
readonly PATH_FILES="${PATH_DIR}/../bin"

source "${PATH_DIR}/utils.sh"
LOG_LVL=1

readonly REQ_PKGS=(hostapd dhcpcd5 dnsmasq iptables)
readonly GIT_RAW="https://raw.githubusercontent.com"
readonly GIT_DHCPCD="${GIT_RAW}/NetworkConfiguration/dhcpcd/master"
readonly GIT_DNSMASQ="${GIT_RAW}/imp/dnsmasq/master"

function main()
{
  log_dbg "Full path: ${PATH_DIR}/${SCRIPT_NAME}\n"

  print_title "Warning"
  log_inf "This script will overwrite:"
  log_inf "- /etc/dhcpcd.conf"
  log_inf "- /etc/dhcpcd.conf.orig"
  log_inf "- /etc/dnsmasq.conf"
  log_inf "- /etc/dnsmasq.conf.orig"
  log_inf ".orig files will be downloaded directly from each respective gits."
  log_inf "This script will also remove duplicate iptables rules."
  log_inf "If needed, backup files before continuing."
  input_yes_or_no "Continue?" "Y"

  # cfg.
  # ---------------------------------------------------------------------------
  print_title "Access Point configuration"
  read -p "Enter AP SSID:`echo $'\n> '`" ap_ssid
  read -sp "Enter AP password:`echo $'\n> '`" ap_password; echo ""
  read -p "Enter AP country code:`echo $'\n> '`" ap_country_code
  log_dbg "ssid: $ap_ssid, passwd: $ap_password, cc: $ap_country_code"

  # exec.
  # ---------------------------------------------------------------------------
  print_title "Setting up routed WAP..."
  log_inf "Installing ${REQ_PKGS[*]}... "
  install_packages ${REQ_PKGS[@]}

  log_inf "Configuring hostapd..."
  sudo cp "${PATH_FILES}/hostapd_routed_ap.conf" /etc/hostapd/
  hostapd_conf="/etc/hostapd/hostapd_routed_ap.conf"
  set_cfg_file_key_value $hostapd_conf ssid "$ap_ssid"
  set_cfg_file_key_value $hostapd_conf wpa_passphrase "$ap_password"
  set_cfg_file_key_value $hostapd_conf country_code "$ap_country_code"
  set_cfg_file_key_value /etc/default/hostapd DAEMON_CONF "\"$hostapd_conf\""

  log_inf "Configuring dhcpcd..."
  sudo wget -qO /etc/dhcpcd.conf.orig "${GIT_DHCPCD}/src/dhcpcd.conf"
  sudo cp "${PATH_FILES}/dhcpcd_routed_ap.conf" /etc/dhcpcd.conf

  log_inf "Configuring dnsmasq..."
  sudo wget -qO /etc/dnsmasq.conf.orig "${GIT_DNSMASQ}/dnsmasq.conf.example"
  sudo cp "${PATH_FILES}/dnsmasq_routed_ap.conf" /etc/dnsmasq.conf

  log_inf "Configuring routing..."
  # Enable ipv4 forwarding
  sudo cp "${PATH_FILES}/sysctl_routed_ap.conf" /etc/sysctl.d/routed-ap.conf
  sudo sysctl -w net.ipv4.ip_forward=1 1> /dev/null

  # Add outbound traffic IP masquerading on eth0, save and load rule @boot
  sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
  delete_duplicate_iptables_rules
  sudo iptables-save | sudo tee /etc/iptables_routed_ap.conf 1> /dev/null
  add_cronjob "@reboot sudo iptables-restore < /etc/iptables_routed_ap.conf"

  log_inf "Starting services..."
  sudo service dhcpcd restart &> /dev/null
  sudo systemctl enable dnsmasq &> /dev/null
  sudo service dnsmasq restart &> /dev/null
  sudo systemctl unmask hostapd &> /dev/null
  sudo systemctl enable hostapd &> /dev/null
  sudo service hostapd restart &> /dev/null

  log_inf "Routed WAP set:"
  log_inf "- SSID: $ap_ssid"
  log_inf "- Router's IP: 192.168.4.1/24, to edit: /etc/dhcpcd.conf"
  log_inf "- Listening interface: wlan0, to edit: /etc/dnsmasq.conf"
  log_inf "- Routes to eth0 using IP masquerading, to edit: iptables"
}

main
