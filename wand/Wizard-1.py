import asyncio
from machine import Pin, PWM
from networking import Networking

class Wizard:
    def __init__(self):
        self.button = Pin(9, Pin.IN)
        self.GREEN = Pin(1,Pin.OUT) #Pin number will be determined later placeholder
        self.RED = Pin(0,Pin.OUT) #Pin number will be determined later placeholder
        self.WHITE = Pin(2, Pin.OUT) #Pin number will be determined later placeholder
        self.hit = 0
        self.msg = ''
        self.beginGame = False
        #Initialise ESPNOW
        self.networking = Networking()
        self.recipient_mac = b'\xFF\xFF\xFF\xFF\xFF\xFF'
        self.totalGametime = 300
        
        

    '''
    Handler function for ESPNOW. Extracts message and stores it in class variable
    '''
    def receive(self):
        # print("Receive")
        for mac, message, rtime in self.networking.aen.return_messages(): #You can directly iterate over the function
            self.msg = message
    
    '''
    Function to handle Wizard health. Each wizard has 1 life. If they are hit
    once they will "die" and not be in the game anymore. Hits are determined based
    on proximity to the Dragon.
    '''
    async def check_health(self):
        while True:
            # Read from ESPNOW
            self.networking.aen.irq(self.receive())
            placeholder = self.networking.aen.rssi()

            try:
                # rssi_value = placeholder[b'T2\x043H\x14'][0] #Cory ESP As Dragon
                rssi_value = placeholder[b'T2\x04!a\x9c'][0] #Jaylen ESP As Dragon
            except KeyError:
                pass

            if self.msg == '!reset':
                self.hit = 0
                self.totalGametime = 300
                self.GREEN.off()
                self.RED.off()
                self.WHITE.off()
                self.beginGame = True
                print("Game has started")

            # if message is detected AND rssi is within the threashold, player gets hit
            if self.msg == 'breathingFire' and rssi_value > -65 and self.beginGame:

                print("HITTTT!")
                self.hit = 1

            # If a player is dead, advertise their ID, if not, put them in jail
            if self.hit == 1 and self.beginGame == True:
                message =  f'im dead'
                self.networking.aen.send(self.recipient_mac, message)
                print(f'Wizard Is Dead', end='\r')
            elif self.hit == 0 and self.beginGame == True:
                print(f'Wizard Is Alive', end='\r')

            # print(rssi_value)
            await asyncio.sleep(0.1)
            
    '''
    Function to handle the LED state:
        Dead: Neopixel Off
        Alive: Solid White
    '''
    async def neoPixel(self):
        while True:
            # Wizard Dead (Neo Off)
            if self.hit == 1:
                self.WHITE.off()
                self.GREEN.off()
                self.RED.on()

            # Wizard in Game (White)
            else:
                self.WHITE.on()
                self.GREEN.off()
                self.RED.off()
            await asyncio.sleep(0.01)
    
    async def gameOver(self):
        while True:
            if self.totalGametime == 0:
                # self.led[0] = RED #Wizards outlasted the timer
                self.WHITE.off()
                self.RED.off()
                self.GREEN.on()
                self.inGame = False
                print("The Wizards wins!")
            await asyncio.sleep(0.01)


    async def timer(self):
        #Timer decrementing till 5 minutes has gone by
        while True:
            if self.totalGametime > 0 and self.beginGame:
                minutes, seconds = divmod(self.totalGametime, 60)
                print(f"Time remaining: {minutes:02d}:{seconds:02d}", end='\r')
                self.totalGametime -= 1
                await asyncio.sleep(1)
            await asyncio.sleep(0.01)

    async def main(self):
        asyncio.create_task(self.check_health())
        asyncio.create_task(self.timer())
        asyncio.create_task(self.gameOver())
        asyncio.create_task(self.neoPixel())
        while True:
            await asyncio.sleep(0.1)

wizard = Wizard()
asyncio.run(wizard.main())