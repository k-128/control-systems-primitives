import smbus2 as smbus


LCD_ADDR = 0x27
LCD_CLEARDISPLAY        = 0x01  # Commands ------------------------------------
LCD_RETURNHOME          = 0x02
LCD_ENTRYMODESET        = 0x04
LCD_DISPLAYCONTROL      = 0x08
LCD_CURSORSHIFT         = 0x10
LCD_FUNCTIONSET         = 0x20
LCD_SETCGRAMADDR        = 0x40
LCD_SETDDRAMADDR        = 0x80
LCD_ENTRYRIGHT          = 0x00  # Flags: Display entry mode -------------------
LCD_ENTRYLEFT           = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00
LCD_DISPLAYON           = 0x04  # Flags: Display on/off controls --------------
LCD_DISPLAYOFF          = 0x00
LCD_CURSORON            = 0x02
LCD_CURSOROFF           = 0x00
LCD_BLINKON             = 0x01
LCD_BLINKOFF            = 0x00
LCD_DISPLAYMOVE         = 0x08  # Flags: Display cursor shift -----------------
LCD_CURSORMOVE          = 0x00
LCD_MOVERIGHT           = 0x04
LCD_MOVELEFT            = 0x00
LCD_8BITMODE            = 0x10  # Flags: Function set -------------------------
LCD_4BITMODE            = 0x00
LCD_2LINE               = 0x08
LCD_1LINE               = 0x00
LCD_5x10DOTS            = 0x04
LCD_5x8DOTS             = 0x00
LCD_BACKLIGHT           = 0x08  # Flags: Backlight control---------------------
LCD_NOBACKLIGHT         = 0x00
En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit


class I2CDevice:
    def __init__(self, i2c_addr: int, port: int=1) -> None:
        self.i2c_addr = i2c_addr
        self.bus = smbus.SMBus(port)

    def write_cmd(self, cmd: int) -> None:
        self.bus.write_byte(self.i2c_addr, cmd)

    def write_cmd_arg(self, cmd: int, data: list) -> None:
        self.bus.write_byte_data(self.i2c_addr, cmd, data)

    def write_block_data(self, cmd: int, data: list) -> None:
        self.bus.write_block_data(self.i2c_addr, cmd, data)

    def read(self):
        return self.bus.read_byte(self.i2c_addr)

    def read_data(self, cmd: int):
        return self.bus.read_byte_data(self.i2c_addr, cmd)

    def read_block_data(self, cmd: int):
        return self.bus.read_block_data(self.i2c_addr, cmd)


class LCD:
    def __init__(self) -> None:
        self.lcd_device = I2CDevice(LCD_ADDR)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x03)
        self.lcd_write(0x02)
        self.lcd_write(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self.lcd_write(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_ENTRYMODESET | LCD_ENTRYLEFT)

    def lcd_strobe(self, data: int) -> None:
        self.lcd_device.write_cmd(data | En | LCD_BACKLIGHT)
        self.lcd_device.write_cmd(((data & ~En) | LCD_BACKLIGHT))

    def lcd_write_four_bits(self, data: int) -> None:
        self.lcd_device.write_cmd(data | LCD_BACKLIGHT)
        self.lcd_strobe(data)

    def lcd_write(self, cmd: int, mode: int=0) -> None:
        self.lcd_write_four_bits(mode | (cmd & 0xF0))
        self.lcd_write_four_bits(mode | ((cmd << 4) & 0xF0))

    def lcd_write_char(self, charvalue: str, mode: int=1) -> None:
        self.lcd_write_four_bits(mode | (charvalue & 0xF0))
        self.lcd_write_four_bits(mode | ((charvalue << 4) & 0xF0))

    def lcd_display_string(self, string: str, line: int) -> None:
        if line == 1:
            self.lcd_write(0x80)
        elif line == 2:
            self.lcd_write(0xC0)
        elif line == 3:
            self.lcd_write(0x94)
        elif line == 4:
            self.lcd_write(0xD4)

        for char in string:
            self.lcd_write(ord(char), Rs)

    def lcd_clear(self) -> None:
        self.lcd_write(LCD_CLEARDISPLAY)
        self.lcd_write(LCD_RETURNHOME)

    def backlight(self, state: int) -> None:
        if state == 0:
            self.lcd_device.write_cmd(LCD_NOBACKLIGHT)
        elif state == 1:
            self.lcd_device.write_cmd(LCD_BACKLIGHT)

    def lcd_load_custom_chars(self, fontdata) -> None:
        self.lcd_write(0x40)
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)

    def lcd_display_string_pos(self, string: str, line: int, pos: int) -> None:
        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
        elif line == 3:
            pos_new = 0x14 + pos
        elif line == 4:
            pos_new = 0x54 + pos

        self.lcd_write(0x80 + pos_new)

        for char in string:
            self.lcd_write(ord(char), Rs)


if __name__ == "__main__":
    from datetime import datetime as dt
    from random import random, randint

    def update_time(lcd: LCD, lcd_width: int) -> None:
        if lcd_width > 18:
            msg = dt.now().strftime("%Y-%m-%d %H:%M")
            msg = (lcd_width - len(msg)) * " " + msg
            lcd.lcd_display_string(msg, 1)
        else:
            msg = dt.now().strftime("%Y-%m-%d %H:%M")
            msg = (lcd_width - len(msg)) * " " + msg
            lcd.lcd_display_string(msg, 1)

    def test(lcd_rows: int = 2, lcd_width: int = 16) -> None:
        lcd = LCD()
        try:
            while True:
                print(f"{dt.now()} - Update")
                update_time(lcd, lcd_width)
                if lcd_rows == 4:
                    msg = f"x: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 2)
                    msg = f"y: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 3)
                    msg = f"z: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 4)
                else:
                    msg = f"x: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 2)
                    sleep(2.4)
                    msg = f"y: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 2)
                    sleep(2.4)
                    msg = f"z: {(random() + randint(0, 1_000)):.2f}"
                    msg = (lcd_width - len(msg)) * " " + msg
                    lcd.lcd_display_string(msg, 2)
                sleep(0.33)
        finally:
            lcd.backlight(0)

    test(4, 20)
