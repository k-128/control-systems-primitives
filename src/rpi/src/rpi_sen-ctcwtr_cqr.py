from time import sleep

import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
SEN = 16  # GPIO 23
GPIO.setup(SEN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


if __name__ == "__main__":
    try:
        while True:
            print(f"State: {GPIO.input(SEN)}")
            sleep(1)
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up.")
