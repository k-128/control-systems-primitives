from time import sleep

import RPi.GPIO as GPIO
import board
import adafruit_tcs34725


# ----
# GPIO
# -----------------------------------------------------------------------------
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
INT = 17  # 11, GPIO 17
LED = 18  # 12, GPIO 18
GPIO.setup(INT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT, initial=GPIO.LOW)


# ---
# i²c
# -----------------------------------------------------------------------------
i2c = board.I2C()
tcs = adafruit_tcs34725.TCS34725(i2c)
tcs.integration_time = 150  # ms: range[2.4, 614.4]
tcs.gain = 4                # 1 | 4 | 16 | 60


if __name__ == "__main__":
    try:
        while True:
            color_raw = tcs.color_raw
            color     = tcs.color
            color_rgb = tcs.color_rgb_bytes
            temp      = tcs.color_temperature
            lux       = tcs.lux
            print(
                f"RGB raw: {color_raw}; " \
                f"RGB 8b/chan: #{color:02X} | {color_rgb}; " \
                f"{temp:.02f} K; {lux:.02f} lux;"
            )
            sleep(1.0)
    finally:
        GPIO.cleanup()
        print(f"GPIO Cleaned up")
