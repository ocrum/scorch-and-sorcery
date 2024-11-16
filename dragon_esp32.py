from machine import Pin, UART
import time
from now import Now

# Dictionary to map AprilTag family + ID to MAC address
# add as many as there are april tags
tag_to_mac = {
    [insert tagFAM,tagID]: [insert corresponding mac address],
    [insert tagFAM,tagID]: [insert corresponding mac address]

}

uart = UART(1, baudrate=115200, tx=Pin(6), rx=Pin(7))

# get uart message from openmv camera (should be tag family and id)
# from dictionary get corresponding mac address
# this is the mac address you are listening to for espnow for movements
# this is the mac address you send !completed to when they solve the puzzle

# does other things like turn on LEDs on control panel when get movement in puzzle right - only for together mode
# dragon moves based on message it gets (up, right, left, down)