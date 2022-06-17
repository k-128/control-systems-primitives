from signal import pause
from datetime import datetime as dt

import RPi.GPIO as GPIO
from gpiozero import Button


# ------
# Config
# -----------------------------------------------------------------------------
INVERTED_RELAYS = True  # If true: LOW is closed and HIGH opened
REL_IN1         = 5     # 29, GPIO  5
REL_IN2         = 6     # 31, GPIO  6
RELS            = (REL_IN1, REL_IN2)
LED_IN1         = 23    # 16, GPIO 23
LED_IN2         = 24    # 18, GPIO 24
LEDS            = (LED_IN1, LED_IN2)
GPIO.setmode(GPIO.BCM)  # GPIO, BCM (Broadcom SOC: GPIO numbers)
GPIO.setup(RELS, GPIO.OUT, initial=GPIO.HIGH if INVERTED_RELAYS else GPIO.LOW)
GPIO.setup(LEDS, GPIO.OUT, initial=GPIO.LOW)
BTN = Button(18)


# ---------
# Execution
# -----------------------------------------------------------------------------
def set_relay(i: int, s: bool) -> None:
    GPIO.output(i, not s if INVERTED_RELAYS else s)


def get_relay_state(i: int) -> None:
    s = GPIO.input(i)
    return not s if INVERTED_RELAYS else s


def alt_states() -> None:
    s = not get_relay_state(RELS[0])
    set_relay(RELS[0], s)
    set_relay(RELS[1], not s)
    GPIO.output(LEDS[0], s)
    GPIO.output(LEDS[1], not s)
    print(f"{dt.now()}\tStates: [0: {s}]\t[1: {not s}]")


def run() -> None:
    BTN.wait_for_press()
    BTN.when_pressed = lambda: alt_states()
    pause()


if __name__ == "__main__":
    try:
        print("Running test...")
        run()
    finally:
        #GPIO.cleanup()  # Handled by gpiozero
        print("GPIO cleaned up")
