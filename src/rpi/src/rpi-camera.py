import asyncio
from os import makedirs
from datetime import datetime as dt
from pathlib import Path
from fractions import Fraction

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from picamera import PiCamera


async def cfg_cam(is_low_light: bool = False) -> PiCamera:
    '''
    Camera config for consistency between shots and low light situations
    '''
    if is_low_light:
        print("Low light mode set, longer shot time")
        cam = PiCamera(
            resolution=(1280, 720),
            framerate=Fraction(1, 6),  # 1/6
            sensor_mode=3
        )
        cam.shutter_speed = 6_000_000
        cam.iso = 800
        await asyncio.sleep(30)
        cam.exposure_mode = "off"
        return cam
    else:
        cam = PiCamera(resolution=(1280, 720), framerate=30)
        cam.iso = 400
        await asyncio.sleep(2)
        cam.shutter_speed = cam.exposure_speed
        cam.exposure_mode = "off"
        g = cam.awb_gains
        cam.awb_mode = "off"
        cam.awb_gains = g
        return cam


def take_picture(cam: PiCamera) -> None:
    p = Path().cwd() / "bin/camera"
    makedirs(p, exist_ok=True)

    date = dt.now().strftime("%Y_%m_%d-%H_%M_%S")
    with open(f"{p}/img-{date}.jpg", "wb") as f:
        cam.capture(f)
        print(f"{dt.now()} - Image captured: {date}")


async def run() -> None:
    is_low_light = False
    cam = await cfg_cam(is_low_light)
    sec = "*/30" if is_low_light else "*/5"
    print("Camera cfg done.")
    scheduler = AsyncIOScheduler()
    scheduler.add_job(take_picture, args=[cam], trigger="cron", second=sec)
    scheduler.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(run())
        loop.run_forever()
    finally:
        loop.close()
