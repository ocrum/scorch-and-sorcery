import machine

class LED:
    """
    Manages LED on and off states using digital pins.
    """
    def __init__(self, pin_num=0):
        """
        Initializes the LED as a digital output.
        """
        self.pin = machine.Pin(pin_num, machine.Pin.OUT)

    def off(self):
        """
        Turns off the LED by setting the pin to low.
        """
        self.pin.value(0)

    def on(self):
        """
        Turns on the LED by setting the pin to high.
        """
        self.pin.value(1)

    def set_brightness(self, brightness):
        """
        Simulates brightness control by turning the LED on or off.
        Note: Digital pins do not support true brightness control.
        """
        if brightness < 0 or brightness > 1:
            print('Brightness out of range: Only values between 0 and 1 valid')
        else:
            if brightness > 0.5:  # Arbitrary threshold to turn on/off the LED
                self.on()
            else:
                self.off()