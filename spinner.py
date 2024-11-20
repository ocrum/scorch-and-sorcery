import time
from machine import Pin, SoftI2C, ADC
from servo import Servo
import random
import ssd1306
import network
from now import Now

i2c = SoftI2C(scl = Pin(7), sda = Pin(6))

screen = ssd1306.SSD1306_I2C(128,64,i2c)
screen.text('Scorch', 40, 15, 1) # to display text
screen.text('and', 50, 25, 1) # to display text
screen.text('Sorcery', 35, 35, 1) # to display text
screen.show()

button = Pin(9, Pin.IN)

pot = ADC(Pin(3))
pot.atten(ADC.ATTN_11DB) # the pin expects a voltage range up to 3.3V
print(pot.read()) #range 0-4095

motor = Servo(Pin(2))

n = Now()
n.connect()
print(n.wifi.config('mac'))

def move_to_random_position():
    target_angle = random.choice([30, 150])
    rotation_time = random.uniform(0.5, 2.0)

    motor.write_angle(target_angle)
    time.sleep(rotation_time)

    # Stop the servo
    motor.write_angle(90)

try:
    while True:
        if not button.value():
            n.publish(b'!reset')
            print("reset")
            move_to_random_position()
            time.sleep(.5)

            pot_val = pot.read()
            if pot_val < 2000:
                n.publish(b'!individual')
                print("individual")
                time.sleep(.5)
            elif pot_val > 2000:
                n.publish(b'!together')
                print("together")
                time.sleep(.5)

except KeyboardInterrupt:
print("Interrupted! Cleaning up...")

finally:
    # Ensure interfaces are deactivated on exit
    n.close()