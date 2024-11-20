from now import Now
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
        self.win_status = ""

        # Initialize I2C
        self.i2c = SoftI2C(scl = Pin(7), sda = Pin(6))

        self.lsm = LSM6DS3(self.i2c)

        self.red = LED(pin_num=0)
        self.green = LED(pin_num=1)
        self.white = LED(pin_num=2)

        self.button = Button(pin_num=9)

        # ESPNOW
        self.n = Now(self.my_callback)
        self.n.connect()
        self.mac = self.n.wifi.config('mac')
        print("MAC Address:", ':'.join('{:02X}'.format(b) for b in self.mac))

    def my_callback(self, msg, mac):
        print(mac, msg)
        self.n.publish(msg, mac)
        win_status = msg

    # Tag game (get from Jaylen & Cory)
    async def tag(self):
        # if in proximity to dragon - rssi:
        # tagged
        tag_state = True
        # led turns red
        self.red.on()
        self.green.off()
        self.white.off()

        self.n.publish(b'!tagged')

    def read_movement_data(self):
        ax, ay, az, gx, gy, gz = self.lsm.get_readings()
        return gz, gx # TODO adjust the axis of rotation

    def determine_spell(self, lr_data, ud_data):
        THRESHOLD = 32764 # TODO tune treshold

        # Count the number of values that meet the criteria for each spell
        counts = {
            Spell.UP: sum(1 for value in ud_data if value <= -THRESHOLD),
            Spell.DOWN: sum(1 for value in ud_data if value >= THRESHOLD),
            Spell.LEFT: sum(1 for value in lr_data if value >= THRESHOLD),
            Spell.RIGHT: sum(1 for value in lr_data if value <= -THRESHOLD)
        }

        max_spell, max_count = max(counts.items(), key=lambda x: x[1])

        return max_spell if max_count > 0 else Spell.OTHER

    # puppet
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
                self.n.publish(b'!' + movement.encode('utf-8'))
                await asyncio.sleep_ms(10) #TODO tune the cool down
                # TODO give feedback on the spell

    # see if won
    async def win_check(self):
        if self.win_status == "!completed":
            self.red.off()
            self.green.on()
            self.white.off()

            self.n.close()

    async def run(self):
        # Run all asynchronous tasks
        while True:
            # Run the tasks concurrently
            await asyncio.gather(
                self.win_check(),
                self.puzzle(),
                self.tag())

# Initialize the Wand object and run the tasks asynchronously
wand = Wand()

# Run the asyncio event loop
asyncio.run(wand.run())