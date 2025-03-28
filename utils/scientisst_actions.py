import threading
import time
from scientisst import ScientISST


def led_pulse(scientisst: ScientISST):
    try:
        led_threading = threading.Thread(target=_led_pulse, args=(scientisst,))
        led_threading.start()
    except ValueError as e:
        print(f"Error: {e}")  # Print the error message


def _led_pulse(scientisst: ScientISST):
    scientisst.trigger([0, 1])
    time.sleep(1)
    scientisst.trigger([0, 0])