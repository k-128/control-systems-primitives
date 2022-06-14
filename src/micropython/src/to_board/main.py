import uasyncio as asyncio
from machine import Pin


async def blink(led: Pin, duration: int):
    '''duration (ms)'''
    while True:
        led.value(not led.value())
        await asyncio.sleep_ms(duration)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        led = Pin(2, Pin.OUT)
        loop.run_until_complete(blink(led, 500))
    finally:
        loop.close()
