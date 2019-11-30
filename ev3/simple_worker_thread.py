import time
import threading

class SimplePeriodicWorkerThread(threading.Thread):

    def __init__(self, thread_name: str, cycle_length_ms: int = 100):
        threading.Thread.__init__(self)
        self.setName(thread_name)
        self._stop_command_received = False
        self._cycle_length_ms = cycle_length_ms

    def _get_current_time_milliseconds(self):
        return int(round(time.time() * 1000))

    def _wait_until_end_of_cycle_time(self, cycle_start_time):
        _cycle_end_time = self._get_current_time_milliseconds()
        _cycle_time = _cycle_end_time - cycle_start_time
        if (_cycle_time < self._cycle_length_ms):
            time.sleep((self._cycle_length_ms - _cycle_time) * 0.001)

    def perform_cycle(self):
        raise NotImplementedError("Please implement this")

    def run(self):
        while (self._stop_command_received == False):
            _cycle_start_time = self._get_current_time_milliseconds()
            self.perform_cycle()
            self._wait_until_end_of_cycle_time(_cycle_start_time)

    def stop(self):
        self._stop_command_received = True
