#!/usr/bin/env bash


# Execution
# -----------------------------------------------------------------------------
function keyboard_interrupt()
{
  printf "\n[ERR]: Keyboard Interrupt.\n" >&2
  exit 1
}

trap keyboard_interrupt SIGINT # SIGTSTP SIGABRT SIGHUP SIGQUIT SIGTERM


# Input
# -----------------------------------------------------------------------------
#######################################
# Arguments:
# - str         : Question
# - str [opt.]  : Default value (Y || N)
# Example:
# - input_yes_or_no "Hello world?"
# Returns:
# - bool: Yes/No
#######################################
input_yes_or_no()
{
  local prompt default reply

  if [[ ${2:-} = "Y" ]]; then
    prompt="Y/n"
    default="Y"
  elif [[ ${2:-} = "N" ]]; then
    prompt="y/N"
    default="N"
  else
    prompt="y/n"
    default=""
  fi

  while true; do
    # Ask the question (without read -p)
    if [[ $default = "Y" ]] || [[ $default = "N" ]]; then
      printf "$1 [$prompt] (default: $default)\n> "
    else
      printf "$1 [$prompt]\n> "
    fi

    # Read the answer (from /dev/tty to handle stdin redirection)
    read -r reply </dev/tty

    # Default?
    if [[ -z $reply ]]; then
      reply=$default
    fi

    # Check if the reply is valid
    case "$reply" in
      Y*|y*) return 0 ;;
      N*|n*) return 1 ;;
    esac
  done
}

export -f input_yes_or_no


# Logging
# -----------------------------------------------------------------------------
# Levels: -1: None, 0: Error, 1: Info, 2: Debug
LOG_LVL=2

#######################################
# Globals:
# - LOG_LVL
# Arguments:
# - str         : text to output
# Outputs:
# - Writes to stderr if LOG_LVL ge 0
#######################################
function log_err()
{
  if [[ $LOG_LVL -ge 0 ]]; then
    printf "[ERR]: $*\n" >&2
  fi
}

export -f log_err

#######################################
# Globals:
# - LOG_LVL
# Arguments:
# - str         : text to output
# Outputs:
# - Writes to stdout if LOG_LVL ge 1
#######################################
function log_inf()
{
  if [[ $LOG_LVL -ge 1 ]]; then
    printf "[INF]: $*\n"
  fi
}

export -f log_inf

#######################################
# Globals:
# - LOG_LVL
# Arguments:
# - str         : text to output
# Outputs:
# - Writes to stdout if LOG_LVL ge 2
#######################################
function log_dbg()
{
  if [[ $LOG_LVL -ge 2 ]]; then
    printf "[DBG]: $*\n"
  fi
}

export -f log_dbg

#######################################
# Arguments:
# - str         : Title
# Outputs:
# - Writes underlined title to stdout
#######################################
function print_title()
{
  printf "\n$1\n"
  printf -- "-%.0s" $(seq 0 $(expr ${#1} - 1))
  printf "\n"
}

export -f print_title


# Utils
# -----------------------------------------------------------------------------
#######################################
# Get array value
# Arguments:
# - array       : Target array
# - int         : Value index
# Outputs
# - Writes value to stdout
#######################################
get_array_value()
{
  local -r arr=$1
  local -r idx=$2
  printf "${arr[$idx]}"
}

#######################################
# Get a cfg file value from a key
# Arguments:
# - str         : Key
# - str         : File path
# Outputs
# - Writes value to stdout
#######################################
function get_cfg_file_value_from_key()
{
  sed -rn "s/^$0=([^\n]+)$/\1/p" $1
}

#######################################
# Update a cfg file key value, or append if it doesn't exists
# Arguments:
# - str         : File path
# - str         : Target key
# - str         : Value
#######################################
function set_cfg_file_key_value()
{
  local -r file=$1
  local -r key=$2
  local -r value=$3

  if ! grep -R "^[#]*\s*${key}=.*" $file > /dev/null; then
    # Key not found, append:
    printf "$key=$value" >> $file
  else
    # Update key
    sudo sed -ir "s|^[#]*\s*${key}=.*|${key}=${value}|" $file
  fi
}

#######################################
# Install given packages while suppressing apt output
# Arguments:
# - array str   : Packages
#######################################
function install_packages()
{
  sudo apt install $@ -yq &> /dev/null
  if [[ $? != 0 ]]; then
    printf "Error installing $@, exiting.\n"
    exit 1
  fi
}

#######################################
# Add given cronjob
# Arguments:
# - str         : Cron job
# Example:
# - add_cronjob "* * * * * ls /"
# Outputs:
# - Write to stdout packages as they're installed
#######################################
function add_cronjob()
{
  local -r tmp_file="/tmp/crontab_bkp"
  crontab -l 1>$tmp_file 2>/dev/null || true # Ignore error if no previous jobs
  printf "$1\n" >> $tmp_file
  crontab $tmp_file
  if [ -f $tmp_file ]; then
    rm $tmp_file
  fi
}

#######################################
# Delete duplicate iptable rules
#######################################
function delete_duplicate_iptables_rules()
{
  local -r tmp_file="/tmp/iptables.conf"
  sudo iptables-save | awk '/^COMMIT$/ { delete x; }; !x[$0]++' > $tmp_file
  sudo iptables -F
  sudo iptables-restore < $tmp_file
  if [ -f $tmp_file ]; then
    rm $tmp_file
  fi
}
