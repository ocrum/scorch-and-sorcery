from machine import Pin, UART
import time, random
from networking import Networking

tag_to_mac = {
    "1": b'T2\x04!\x83 ',
    "2": b'T2\x04![X ',
    "3": b'T2\x043H\x14 '
}

class Puppet:
    def __init__(self):
        self.RX_PIN = 17  # Receiver pin
        self.TX_PIN = 16  # Transmitter pin
        self.BAUD = 19200  # Baud rate

        self.uart = UART(1, baudrate=self.BAUD, tx=Pin(self.TX_PIN), rx=Pin(self.RX_PIN))

        self.tag_id = ""

        self.final_mac = b'\x00\x00\x00\x00\x00\x00'
        self.final_msg = ''

        self.networking = Networking()

        self.one_done = False
        self.two_done = False

        self.movements = ["!head", "!wings", "!legs", "!tail"]

        self.individual = True

    def parse_message(self, message):
        parts = message.split(",")
        if len(parts) == 2:
            family = parts[0]
            if family == "TAG36H11":
                self.tag_id = parts[1]

    def receive(self):
        print("Receive")
        for mac, message, rtime in self.networking.aen.return_messages(): #You can directly iterate over the function
            self.final_mac = mac
            self.final_msg = message

    def movement(self, msg):
        if msg == "!head":
            # move servo
            print("head moves")
        elif msg == "!legs":
            # move servo
            print("legs move")
        elif msg == "wings":
            # move servo
            print("wings move")
        elif msg == "!tail":
            # move servo
            print("tail moves")
        else:
            print("unknown message")

    def puzzle(self, msg):
        sequence = []
        while len(sequence) < 3:
            candidate = random.randint(0, len(self.movements) - 1)  # Get random index
            if candidate not in sequence:
                sequence.append(candidate)

        sequence = [self.movements[i] for i in sequence]  # Convert indices to elements

        # Your logic
        if msg == sequence[0]:
            self.movement(msg)
            self.one_done = True
        if msg == sequence[1] and self.one_done:
            self.movement(msg)
            self.two_done = True
        if msg == sequence[2] and self.one_done and self.two_done:
            self.movement(msg)
            self.networking.aen.send(b'\xff\xff\xff\xff\xff\xff', "!completed")

    def run(self):
        info = self.uart.read(30)  # Reads up to 30 bytes
        time.sleep_ms(1000)
        if info:  # Check if a message was received
            decoded_info = info.decode('ascii')  # Decode byte to string
            print(f"Received message: {decoded_info}")

            # Parse the message to extract the tag ID
            self.parse_message(decoded_info)
            print(self.tag_id)
        if self.tag_id:
            print(f"Received tag ID: {self.tag_id}")

            mac_address = tag_to_mac.get(self.tag_id)

            self.networking.aen._irq(self.receive())

            if self.final_msg == "!individual":
                self.individual = True
            elif self.final_msg == "!together":
                self.individual = False

            print(self.final_mac)
            print(mac_address)

            b_mac_address = bytes(mac_address, 'utf-8')

            print(type(self.final_mac))

            if self.final_mac == b_mac_address:
                if self.individual = True:
                    self.movement(self.final_msg)
                else:
                    self.puzzle(self.final_msg)

puppet = Puppet()
while True:
    puppet.run()
