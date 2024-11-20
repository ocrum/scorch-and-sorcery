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
        self.win_status = ""

        # Initialize I2C
        self.i2c = SoftI2C(scl=Pin(7), sda=Pin(6))
        self.lsm = LSM6DS3(self.i2c)

        # Initialize LEDs
        self.red = LED(pin_num=0)
        self.green = LED(pin_num=1)
        self.white = LED(pin_num=2)

        # Initialize Button
        self.button = Button(pin_num=9)

        # Initialize Networking
        self.networking = Networking()
        self.networking.initialize()  # Method to set up networking parameters
        self.networking.start()        # Start the networking interface
        self.mac = self.networking.get_mac()
        print("MAC Address:", ':'.join('{:02X}'.format(b) for b in self.mac))

        # Set the recipient MAC address (broadcast in this case)
        self.recipient_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF'

        # Initialize RSSI threshold
        self.RSSI_THRESHOLD = -65  # Example threshold value

    async def handle_incoming_messages(self):
        while True:
            messages = self.networking.receive()
            for msg, mac, rssi in messages:
                decoded_msg = msg.decode('utf-8')
                print(f"Received from {':'.join('{:02X}'.format(b) for b in mac)}: {decoded_msg} with RSSI {rssi}")
                self.win_status = decoded_msg

                # Handle specific messages
                if decoded_msg == "!completed":
                    await self.handle_win()
                elif decoded_msg == "!tagged":
                    await self.handle_tagged()
                else:
                    # Handle other spells or commands
                    pass
            await asyncio.sleep(0.1)  # Adjust the polling interval as needed

    async def handle_tagged(self):
        # Logic when the wand is tagged
        self.tag_state = True
        self.red.on()
        self.green.off()
        self.white.off()
        print("Wand has been tagged!")

    async def handle_win(self):
        # Logic when the game is won
        self.red.off()
        self.green.on()
        self.white.off()
        print("The Wizards win!")
        self.networking.stop()  # Properly stop the networking interface

    async def tag(self):
        if not self.tag_state:
            # Check proximity based on RSSI if necessary
            # For simplicity, tagging action is triggered manually or via some condition
            self.tag_state = True
            self.red.on()
            self.green.off()
            self.white.off()

            # Send a tagged message to all
            self.networking.send(self.recipient_mac, b'!tagged')
            print("Tagged and sent '!tagged' message")

    def read_movement_data(self):
        ax, ay, az, gx, gy, gz = self.lsm.get_readings()
        return gz, gx  # Adjust the axis of rotation as needed

    def determine_spell(self, lr_data, ud_data):
        THRESHOLD = 32764  # Tune threshold as needed

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
                print("Detected an unknown spell")
            else:
                print(f"Detected spell: {movement}")
                spell_message = f"!{movement}".encode('utf-8')
                self.networking.send(self.recipient_mac, spell_message)
                await asyncio.sleep_ms(10)  # Tune the cooldown as needed
                # TODO: Provide feedback on the spell (e.g., LED indicators)

    async def win_check(self):
        if self.win_status == "!completed":
            await self.handle_win()

    async def run(self):
        # Create tasks for handling incoming messages, puzzles, and tagging
        await asyncio.gather(
            self.handle_incoming_messages(),
            self.puzzle(),
            self.tag()
        )

# Initialize the Wand object and run the tasks asynchronously
wand = Wand()

# Run the asyncio event loop
asyncio.run(wand.run())