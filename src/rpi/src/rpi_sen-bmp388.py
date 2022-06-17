from time import sleep
from typing import Tuple

import smbus2 as smbus


# BMP388 I2C address
I2C_ADD_BMP388_AD0_LOW      = 0x76
I2C_ADD_BMP388_AD0_HIGH     = 0x77
I2C_ADD_BMP388              = I2C_ADD_BMP388_AD0_LOW

BMP388_REG_ADD_WIA          = 0x00
BMP388_REG_VAL_WIA          = 0x50

BMP388_REG_ADD_ERR          = 0x02
BMP388_REG_VAL_FATAL_ERR    = 0x01
BMP388_REG_VAL_CMD_ERR      = 0x02
BMP388_REG_VAL_CONF_ERR     = 0x04

BMP388_REG_ADD_STATUS       = 0x03
BMP388_REG_VAL_CMD_RDY      = 0x10
BMP388_REG_VAL_DRDY_PRESS   = 0x20
BMP388_REG_VAL_DRDY_TEMP    = 0x40

BMP388_REG_ADD_CMD          = 0x7E
BMP388_REG_VAL_EXTMODE_EN   = 0x34
BMP388_REG_VAL_FIFI_FLUSH   = 0xB0
BMP388_REG_VAL_SOFT_RESET   = 0xB6

BMP388_REG_ADD_PWR_CTRL     = 0x1B
BMP388_REG_VAL_PRESS_EN     = 0x01
BMP388_REG_VAL_TEMP_EN      = 0x02
BMP388_REG_VAL_NORMAL_MODE  = 0x30

BMP388_REG_ADD_PRESS_XLSB   = 0x04
BMP388_REG_ADD_PRESS_LSB    = 0x05
BMP388_REG_ADD_PRESS_MSB    = 0x06
BMP388_REG_ADD_TEMP_XLSB    = 0x07
BMP388_REG_ADD_TEMP_LSB     = 0x08
BMP388_REG_ADD_TEMP_MSB     = 0x09

BMP388_REG_ADD_T1_LSB       = 0x31
BMP388_REG_ADD_T1_MSB       = 0x32
BMP388_REG_ADD_T2_LSB       = 0x33
BMP388_REG_ADD_T2_MSB       = 0x34
BMP388_REG_ADD_T3           = 0x35
BMP388_REG_ADD_P1_LSB       = 0x36
BMP388_REG_ADD_P1_MSB       = 0x37
BMP388_REG_ADD_P2_LSB       = 0x38
BMP388_REG_ADD_P2_MSB       = 0x39
BMP388_REG_ADD_P3           = 0x3A
BMP388_REG_ADD_P4           = 0x3B
BMP388_REG_ADD_P5_LSB       = 0x3C
BMP388_REG_ADD_P5_MSB       = 0x3D
BMP388_REG_ADD_P6_LSB       = 0x3E
BMP388_REG_ADD_P6_MSB       = 0x3F
BMP388_REG_ADD_P7           = 0x40
BMP388_REG_ADD_P8           = 0x41
BMP388_REG_ADD_P9_LSB       = 0x42
BMP388_REG_ADD_P9_MSB       = 0x43
BMP388_REG_ADD_P10          = 0x44
BMP388_REG_ADD_P11          = 0x45


class BMP388:
    def _read_byte(self, reg: int) -> int:
        return self._bus.read_byte_data(self._address, reg)

    def _read_s8(self, reg: int) -> int:
        result = self._read_byte(reg)
        if result > 128:
            result -= 256
        return result

    def _read_u16(self, reg: int) -> int:
        LSB = self._bus.read_byte_data(self._address, reg)
        MSB = self._bus.read_byte_data(self._address, reg + 1)
        return (MSB << 8) + LSB

    def _read_s16(self, reg: int) -> int:
        result = self._read_u16(reg)
        if result > 32_767:
            result -= 65_536
        return result

    def _write_byte(self, reg: int, val: int) -> None:
        self._bus.write_byte_data(self._address, reg, val)

    def __init__(self, address: int=I2C_ADD_BMP388) -> None:
        self._address = address
        self._bus = smbus.SMBus(1)

        # Load calibration values
        if self._read_byte(BMP388_REG_ADD_WIA) == BMP388_REG_VAL_WIA:
            print("Calibrating BMP388\r\n")
            u8RegData = self._read_byte(BMP388_REG_ADD_STATUS)
            if (u8RegData & BMP388_REG_VAL_CMD_RDY):
                self._write_byte(BMP388_REG_ADD_CMD, BMP388_REG_VAL_SOFT_RESET)
                sleep(0.01)
        else:
            print("Pressure sensor NULL\r\n")

        self._write_byte(
            BMP388_REG_ADD_PWR_CTRL,
            BMP388_REG_VAL_PRESS_EN
            | BMP388_REG_VAL_TEMP_EN
            | BMP388_REG_VAL_NORMAL_MODE
        )

        # Read the temperature calibration parameters
        self.T1   = self._read_u16(BMP388_REG_ADD_T1_LSB)
        self.T2   = self._read_u16(BMP388_REG_ADD_T2_LSB)
        self.T3   = self._read_s8(BMP388_REG_ADD_T3)

        # Read the pressure calibration parameters
        self.P1   = self._read_s16(BMP388_REG_ADD_P1_LSB)
        self.P2   = self._read_s16(BMP388_REG_ADD_P2_LSB)
        self.P3   = self._read_s8(BMP388_REG_ADD_P3)
        self.P4   = self._read_s8(BMP388_REG_ADD_P4)
        self.P5   = self._read_u16(BMP388_REG_ADD_P5_LSB)
        self.P6   = self._read_u16(BMP388_REG_ADD_P6_LSB)
        self.P7   = self._read_s8(BMP388_REG_ADD_P7)
        self.P8   = self._read_s8(BMP388_REG_ADD_P8)
        self.P9   = self._read_s16(BMP388_REG_ADD_P9_LSB)
        self.P10  = self._read_s8(BMP388_REG_ADD_P10)
        self.P11  = self._read_s8(BMP388_REG_ADD_P11)

    def _get_compensated_temperature(self, adc_t: float) -> float:
        partial_data1 = adc_t - (256 * self.T1)
        partial_data2 = self.T2 * partial_data1
        partial_data3 = partial_data1 * partial_data1
        partial_data4 = partial_data3 * self.T3
        partial_data5 = partial_data2 * 262_144 + partial_data4
        partial_data6 = partial_data5 / 4_294_967_296
        self.T_fine = partial_data6
        return partial_data6 * 25 / 16_384

    def _get_compensated_pressure(self, adc_p: float) -> float:
        partial_data1 = self.T_fine * self.T_fine
        partial_data2 = partial_data1 / 64
        partial_data3 = partial_data2 * self.T_fine / 256
        partial_data4 = self.P8 * partial_data3 / 32
        partial_data5 = self.P7 * partial_data1 * 16
        partial_data6 = self.P6 * self.T_fine * 4_194_304
        offset = self.P5 * 140_737_488_355_328 \
            + partial_data4 + partial_data5 + partial_data6

        partial_data2 = self.P4 * partial_data3 / 32
        partial_data4 = self.P3 * partial_data1 * 4
        partial_data5 = self.P2 - 16_384 * self.T_fine * 2_097_152
        sensitivity = (self.P1 - 16_384) * 70_368_744_177_664 \
            + partial_data2 + partial_data4 + partial_data5

        partial_data1 = sensitivity / 16_777_216 * adc_p
        partial_data2 = self.P10 * self.T_fine
        partial_data3 = partial_data2 + 65_536 * self.P9
        partial_data4 = partial_data3 * adc_p / 8_192
        partial_data5 = partial_data4 * adc_p / 512
        partial_data6 = adc_p * adc_p
        partial_data2 = self.P11 * partial_data6 / 65_536
        partial_data3 = partial_data2 * adc_p / 128
        partial_data4 = offset / 4 \
            + partial_data1 + partial_data5 + partial_data3
        return partial_data4 * 25 / 1_099_511_627_776

    def get_data(self) -> Tuple[float, float, float]:
        """Returns temperature (°C), pressure (Pa) and altitude (m)

        Output: (float, float, float)
        - 96_386.2 Pa = 963.862 hPa = 0.963862 bar
        """
        xlsb  = self._read_byte(BMP388_REG_ADD_TEMP_XLSB)
        lsb   = self._read_byte(BMP388_REG_ADD_TEMP_LSB)
        msb   = self._read_byte(BMP388_REG_ADD_TEMP_MSB)
        adc_T = (msb << 16) + (lsb << 8) + (xlsb)
        temp  = self._get_compensated_temperature(adc_T)
        xlsb  = self._read_byte(BMP388_REG_ADD_PRESS_XLSB)
        lsb   = self._read_byte(BMP388_REG_ADD_PRESS_LSB)
        msb   = self._read_byte(BMP388_REG_ADD_PRESS_MSB)

        adc_P = (msb << 16) + (lsb << 8) + (xlsb)
        pressure = self._get_compensated_pressure(adc_P)
        altitude = 4_433_000 * (1 - pow(((pressure / 100) / 101_325), 0.1903))
        return temp, pressure, altitude


if __name__ == "__main__":
    bmp388 = BMP388()
    while True:
        t, p, a = bmp388.get_data()
        print(f"{t / 100:.1f}°C\t{p / 100:.2f}hPa\t{(a / 100):.2f}m")
        sleep(1)
