import board
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont, ImageChops


I2C                   = board.I2C()
SSD1306_DFLT_I2C_ADDR = 0x3C


class SSD1306_I2C:
    """
    SSD1306 i²c OLED Screen
    """

    def __init__(
        self,
        width: int      = 128,
        height: int     = 64,
        i2c_addr: int   = SSD1306_DFLT_I2C_ADDR
    ) -> None:
        self.width      = width
        self.height     = height
        self.i2c_addr   = i2c_addr

        # Reset display
        self.screen = adafruit_ssd1306.SSD1306_I2C(
            width,
            height,
            I2C,
            addr=i2c_addr
        )
        self.reset_screen()

        # Set blank image
        self.image = Image.new("1", (width, height))
        self._draw = ImageDraw.Draw(self.image)

    def __del__(self) -> None:
        if self.screen:
            self.reset_screen()

    def __repr__(self) -> str:
        return f"SSD1306[{self.i2c_addr}, {self.width}, {self.height}]"

    @property
    def draw(self) -> ImageDraw.Draw:
        return self._draw

    def reset_screen(self) -> None:
        self.screen.fill(0)
        self.screen.show()

    def display_image(self) -> None:
        self.screen.image(self.image)
        self.screen.show()

    def invert_image(self) -> None:
        self.image = ImageChops.invert(self.image)
        self._draw = ImageDraw.Draw(self.image)
        self.display_image()


if __name__ == "__main__":
    from time import sleep
    from datetime import datetime as dt
    from random import random, randint

    print("Init tests...")
    try:
        w           = 128
        h           = 64
        font_size   = 12
        line_h      = font_size + 2
        screen_dur  = 1

        ssd1306 = SSD1306_I2C()
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            font_size
        )

        while True:
            # --------
            # Screen 0
            # -----------------------------------------------------------------
            ssd1306.draw.rectangle((0, 0, w, h), 0, 0)
            msg = dt.now().strftime("%Y-%m-%d %H:%M")
            ssd1306.draw.text(
                (0, 0), msg, fill=255, font=font, anchor="la", align="left"
            )
            msg = "-" * 12
            msg_w, msg_h = font.getsize(msg)
            xy = (ssd1306.screen.width // 2 - msg_w // 2, 1 * line_h)
            ssd1306.draw.text(xy, msg, 255, font)
            ssd1306.display_image()
            sleep(screen_dur)

            # --------
            # Screen 1
            # -----------------------------------------------------------------
            ssd1306.draw.rectangle((0, 0, w, h), 0, 0)
            msg =   f"{dt.now().strftime('%Y-%m-%d %H:%M')}\n"
            msg +=  f"a: {(random() + randint(0, 1_000_000)):.2f} %\n"
            msg +=  f"b: {(random() + randint(0, 1_000_000)):.2f}{chr(223)}K\n"
            msg +=  f"c: {(random() + randint(0, 1_000_000)):.2f}"
            ssd1306.draw.multiline_text(
                (w, 0), msg, 255, font, anchor="ra", align="right", spacing=3
            )
            ssd1306.display_image()
            sleep(screen_dur)

            # --------
            # Screen 2
            # -----------------------------------------------------------------
            ssd1306.draw.rectangle((0, 0, w, h), 0, 0)
            msg =   f"{dt.now().strftime('%Y-%m-%d %H:%M')}\n"
            msg +=  f"x: {(random() * randint(-1_000, 100)):.2f}\n"
            msg +=  f"y: {(random() * randint(-1_000, 100)):.2f}\n"
            msg +=  f"z: {(random() * randint(-1_000, 100)):.2f}"
            ssd1306.draw.multiline_text(
                (w, 0), msg, 255, font, anchor="ra", align="right", spacing=3
            )
            ssd1306.display_image()
            sleep(screen_dur)

            # --------
            # Screen 3
            # -----------------------------------------------------------------
            ssd1306.invert_image()
            sleep(screen_dur)

    except Exception as e:
        print(f"{e}")
