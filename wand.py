from now import Now
import time
from machine import Pin, SoftI2C, ADC
import random
import asyncio


class Wand:
    def __init__(self):
        # Initialize the LED
        RED_PIN = 0
        GREEN_PIN = 1
        BLUE_PIN = 2

        red = PWM(Pin(RED_PIN), freq=1000)
        green = PWM(Pin(GREEN_PIN), freq=1000)
        blue = PWM(Pin(BLUE_PIN), freq=1000)

        # whether or not tagged
        tag_state = False

        # start with a white LED on the wand
        self.led(255,255,255)

        # start assuming in individual mode
        individual = True

        # button status
        button_status = False

        # I2C address of the MPU-6050 sensor
        MPU6050_ADDR = 0x68

        # MPU-6050 register addresses
        PWR_MGMT_1 = 0x6B
        ACCEL_XOUT_H = 0x3B
        ACCEL_YOUT_H = 0x3D
        ACCEL_ZOUT_H = 0x3F
        GYRO_XOUT_H = 0x43
        GYRO_YOUT_H = 0x45
        GYRO_ZOUT_H = 0x47

        # Initialize I2C
        i2c = I2C(1, scl=Pin(5), sda=Pin(4), freq=400000)
        i2c.writeto_mem(MPU6050_ADDR, PWR_MGMT_1, b'\x00')

        movement = ""

        win_status = ""

        # ESPNOW
        n = Now(self.my_callback)
        n.connect()
        print(n.wifi.config('mac'))

    def my_callback(self, msg, mac):
        print(mac, msg)
        n.publish(msg, mac)
        win_status = msg

    # pass in RGB values
    def led(self, r, g, b):
        red.duty(int(r * 4))
        green.duty(int(g * 4))
        blue.duty(int(b * 4))

    def read_raw_data(addr):
        high = i2c.readfrom_mem(MPU6050_ADDR, addr, 1)
        low = i2c.readfrom_mem(MPU6050_ADDR, addr + 1, 1)
        value = (high[0] << 8) | low[0]
        if value > 32767:
            value -= 65536
        return value

    def get_sensor_data():
        # Read accelerometer data
        accel_x = read_raw_data(ACCEL_XOUT_H)
        accel_y = read_raw_data(ACCEL_YOUT_H)
        accel_z = read_raw_data(ACCEL_ZOUT_H)

        # Read gyroscope data
        gyro_x = read_raw_data(GYRO_XOUT_H)
        gyro_y = read_raw_data(GYRO_YOUT_H)
        gyro_z = read_raw_data(GYRO_ZOUT_H)

        # Convert raw data to g's and degrees per second
        accel_x = accel_x / 16384.0
        accel_y = accel_y / 16384.0
        accel_z = accel_z / 16384.0

        gyro_x = gyro_x / 131.0
        gyro_y = gyro_y / 131.0
        gyro_z = gyro_z / 131.0

        # determine what values are up
        if [insert wanted values of gyro & accelerometer]:
            movement = "up"
        # determine what values are down
        elif [insert wanted values of gyro & accelerometer]:
            movement = "down"
        # determine what values are right
        elif [insert wanted values of gyro & accelerometer]:
            movement = "right"
        # determine what values are left
        if [insert wanted values of gyro & accelerometer]:
            movement = "left"

        return movement

    # Tag game (get from Jaylen & Cory)
    async def tag(self):
        # if in proximity to dragon - rssi:
        # tagged
        tag_state = True
        # led turns red
        self.led(255,0,0)
        n.publish(b'!tagged')

    # puppet
    async def puppet(self):
        if button_status == True:
            self.led(255,255,0) # yellow
            movement = self.get_sensor_data()
            if movement == "up": # inidcating up with accel and gyro values
                n.publish(b'!up')
                await asyncio.sleep(1)
            elif : # indicating down with accel and gyro values
                n.publish(b'!down')
                await asyncio.sleep(1)
            elif : # indicating right with accel and gyro values
                n.publish(b'!right')
                await asyncio.sleep(1)
            elif : # indicating left with accel and gyro values
                n.publish(b'!left')
                await asyncio.sleep(1)
            else:
                self.led(255,255,255) # white

    # see if won
    async def win_check(self):
        if win_status == "!completed":
            self.led(255,255,0)
            n.close()

    async def run(self):
        # Run all asynchronous tasks
        while True:
            # Run the tasks concurrently
            await asyncio.gather(
                self.win_check(),
                self.puppet(),
                self.tag()
            )


# Initialize the Wand object and run the tasks asynchronously
wand = Wand()

# Run the asyncio event loop
asyncio.run(wand.run())