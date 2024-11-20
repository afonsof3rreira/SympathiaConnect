import threading
import time


def led_pulse(scientisst):
    led_threading = threading.Thread(target=_led_pulse, args=(scientisst,))
    led_threading.start()


def _led_pulse(scientisst):
    scientisst.trigger([0, 1])
    time.sleep(1)
    scientisst.trigger([0, 0])