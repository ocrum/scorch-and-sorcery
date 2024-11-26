from networking import Networking
from machine import Pin, SoftI2C, ADC, PWM
import asyncio
from lsm6ds3 import LSM6DS3
from button import Button
from led import LED

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
        self.tag_state = False     # whether tagged
        self.game_mode = GameMode.S_and_S
        self.msg = ""

        # Initialize I2C
        self.i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.lsm = LSM6DS3(self.i2c)

        self.red = LED(pin_num=0)
        self.green = LED(pin_num=1)
        self.white = LED(pin_num=2)

        self.button = Button(pin_num=9)

        # Networking
        self.networking = Networking()

    def my_callback(self):
        for mac, message, rtime in self.networking.aen.return_messages(): #You can directly iterate over the function
            self.msg = message

    async def tag(self):
        # If in proximity to dragon - rssi:
        self.tag_state = True
        # LED turns red
        self.red.on()
        self.green.off()
        self.white.off()

        # self.networking.send(b'\xFF\xFF\xFF\xFF\xFF\xFF', b'!tagged')

    def read_movement_data(self):
        ax, ay, az, gx, gy, gz = self.lsm.get_readings()
        return gz, gx # TODO adjust the axis of rotation

    def determine_spell(self, lr_data, ud_data):
        THRESHOLD = 32764 # TODO tune treshold

        counts = {
            Spell.UP: sum(1 for value in ud_data if value <= -THRESHOLD),
            Spell.DOWN: sum(1 for value in ud_data if value >= THRESHOLD),
            Spell.LEFT: sum(1 for value in lr_data if value >= THRESHOLD),
            Spell.RIGHT: sum(1 for value in lr_data if value <= -THRESHOLD)
        }

        max_spell, max_count = max(counts.items(), key=lambda x: x[1])
        return max_spell if max_count > 0 else Spell.OTHER

    async def puzzle(self):
        if self.game_mode != GameMode.INFERNO and self.button.is_pressed():
            lr_data = []
            ud_data = []
            while self.button.is_being_pressed():
                await asyncio.sleep_ms(10)
                gz, gx = self.read_movement_data()
                lr_data.append(gz)
                ud_data.append(gx)

            movement = self.determine_spell(lr_data, ud_data)

            if movement == Spell.OTHER:
                print("other spell")
            else:
                print(movement)
                self.networking.aen.send(b'\xFF\xFF\xFF\xFF\xFF\xFF', b'!' + movement)
                await asyncio.sleep_ms(10)  # Tune the cooldown as needed

    async def win_check(self):
        if self.msg == "!completed":
            self.red.off()
            self.green.on()
            self.white.off()

    async def run(self):
        while True:
            self.my_callback()
            await asyncio.gather(
                self.win_check(),
                self.puzzle(),
                self.tag()
            )

# Initialize the Wand object and run the tasks asynchronously
wand = Wand()
asyncio.run(wand.run())