from ev3dev2.button import Button
from ev3.simple_worker_thread import SimplePeriodicWorkerThread

class EV3Buttons(SimplePeriodicWorkerThread):

    def __init__(self):
        super().__init__(thread_name='EV3Buttons')
        self._buttons = Button()
        self._enter_button_listener = None
        self._esc_button_listener = None

    def add_enter_button_listener(self, enter_button_listener: callable):
        self._enter_button_listener = enter_button_listener

    def remove_enter_button_listener(self):
        self._enter_button_listener = None

    def add_esc_button_listener(self, esc_button_listener: callable):
        self._esc_button_listener = esc_button_listener

    def remove_esc_button_listener(self):
        self._esc_button_listener = None

    def perform_cycle(self):
        if (not (self._enter_button_listener is None)) and self._buttons.enter:
            self._enter_button_listener()
        elif (not (self._esc_button_listener is None)) and self._buttons.backspace:
            self._esc_button_listener()
