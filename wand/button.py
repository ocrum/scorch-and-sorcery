import machine

class Button:
    """
    Manages the button input.
    Detects button presses by comparing the current and previous states.
    """
    def __init__(self, pin_num=20):
        """
        Initializes the button with the specified pin and sets the initial state.
        """
        self.button = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
        self.prev_state = self.button.value()

    def is_pressed(self):
        """
        Checks if the button was pressed (transitions from unpressed to pressed).
        :return: True if the button is newly pressed, False otherwise
        """
        current_state = self.button.value()
        ret_val = False

        # New press when curr value is pressed (0) and prev is unpressed (1)
        if current_state == 0 and self.prev_state == 1:
            ret_val = True

        self.prev_state = self.button.value()
        return ret_val

    def is_being_pressed(self):
        return self.button.value() == 0
