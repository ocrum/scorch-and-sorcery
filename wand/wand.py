from now import Now
from machine import Pin, SoftI2C, ADC, PWM
import asyncio
from adxl345 import ADXL345
from lsm6ds3 import LSM6DS3
from button import Button

class GameMode:
    S_and_S = "scorch & sorcery"
    INFERNO = "inferno chase"
    PUZZLE = "puzzle"

class Spell:
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    OTHER = "other"

class Wand:
    def __init__(self):
        # Initialize the LED
        RED_PIN = 0
        GREEN_PIN = 1
        BLUE_PIN = 2

        self.red = PWM(Pin(RED_PIN), freq=1000)
        self.green = PWM(Pin(GREEN_PIN), freq=1000)
        self.blue = PWM(Pin(BLUE_PIN), freq=1000)
        self.led(255,255,255) # start with a white LED on the wand

        self.tag_state = False     # whether tagged
        self.game_mode = GameMode.S_and_S

        self.button = Button(pin_num=9)

        self.win_status = ""

        # Initialize I2C
        self.i2c = SoftI2C(scl = Pin(7), sda = Pin(6))

        # Accelerometer
        self.using_lsm6ds3 = False
        if self.using_lsm6ds3:
            self.lsm = LSM6DS3(self.i2c)
        else:
            self.adx = ADXL345(self.i2c)

        # ESPNOW
        self.n = Now(self.my_callback)
        self.n.connect()
        self.mac = self.n.wifi.config('mac')
        print("MAC Address:", ':'.join('{:02X}'.format(b) for b in self.mac))

    def my_callback(self, msg, mac):
        print(mac, msg)
        self.n.publish(msg, mac)
        win_status = msg

    # pass in RGB values
    def led(self, r, g, b):
        self.red.duty(int(r * 4))
        self.green.duty(int(g * 4))
        self.blue.duty(int(b * 4))

    # Tag game (get from Jaylen & Cory)
    async def tag(self):
        # if in proximity to dragon - rssi:
        # tagged
        tag_state = True
        # led turns red
        self.led(255,0,0)
        self.n.publish(b'!tagged')

    def read_movement_data(self):
        gx = gy = gz = None
        if self.using_lsm6ds3:
            ax, ay, az, gx, gy, gz = self.lsm.get_readings()
        else:
            ax = self.adx.xValue
            ay = self.adx.yValue
            az = self.adx.zValue

        return ax, ay, az, gx, gy, gz

    def determine_spell(self, data):
        """
        Given accelerometer and gyroscope data, determine the spell
        :param data: An array of tuples (ax, ay, az, gx, gy, gz)
        :return: A Spell type
        """
        # The idea, average out the force
        # An up spell should have average large positive az
        return Spell.OTHER


    # puppet
    async def puzzle(self):
        if self.game_mode != GameMode.INFERNO and self.button.is_pressed():
            self.led(255,255,0) # yellow

            data = []
            while self.button.is_being_pressed():
                await asyncio.sleep(0.1)
                data.append(self.read_movement_data())

            movement = self.determine_spell(data)

            if movement == Spell.OTHER:
                self.led(255,255,255) # white
            else:
                self.n.publish(b'!' + movement.encode('utf-8'))
                await asyncio.sleep(1)

    # see if won
    async def win_check(self):
        if self.win_status == "!completed":
            self.led(255,255,0)
            self.n.close()

    async def run(self):
        # Run all asynchronous tasks
        while True:
            # Run the tasks concurrently
            await asyncio.gather(
                self.win_check(),
                self.puzzle(),
                self.tag(),
            )

# Initialize the Wand object and run the tasks asynchronously
wand = Wand()

# Run the asyncio event loop
asyncio.run(wand.run())