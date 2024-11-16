import time
import sensor
import image
import pyb

# Initialize sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)  # Set color format to RGB565
sensor.set_framesize(sensor.QQVGA)  # Set resolution to QQVGA (160x120)
sensor.skip_frames(time=2000)  # Wait for the sensor to initialize
sensor.set_auto_gain(False)  # Turn off auto gain to prevent image washout
sensor.set_auto_whitebal(False)  # Turn off auto white balance to prevent washout

# Initialize UART
uart = pyb.UART(3, baudrate=115200, pins=("P4", "P5"))  # P4 is TX, P5 is RX

while True:
    img = sensor.snapshot()

    for tag in img.find_apriltags():
        img.draw_rectangle(tag.rect(), color=(255, 0, 0))
        img.draw_cross(tag.cx(), tag.cy(), color=(0, 255, 0))

        # Get the tag family and ID
        tag_family = tag.family()
        tag_id = tag.id()

        message = "{}{}".format(tag_family, tag_id)

    uart.write(message.encode('utf-8'))  # Ensure message is encoded as bytes

time.sleep_ms(100)