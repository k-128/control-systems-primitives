from glob import glob


def read_ds18b20() -> float:
    temp = -273.15
    try:
        p = glob("/sys/bus/w1/devices/" + "28*")[0] + "/temperature"
        with open(p, "r") as f:
            temp = float(f.read()) / 1_000
    except Exception as e:
        print(f"{e}")
    return temp


if __name__ == "__main__":
    from time import sleep

    while True:
        print(f"{read_ds18b20()}°C")
        sleep(1)
