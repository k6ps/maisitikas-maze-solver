import sys
from unittest.mock import MagicMock


class Ev3devTestUtil(object):

    @staticmethod
    def create_fake_ev3dev2_module():
        sys.modules["ev3dev2"] = MagicMock()
        sys.modules["ev3dev2.sensor"] = MagicMock()
        sys.modules["ev3dev2.sensor.lego"] = MagicMock()
