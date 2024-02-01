class dac_control:

    def __init__(self, adc_ext_read, dac_value):
        self.scale_factor = 10 ** 3
        if adc_ext_read < 300 * self.scale_factor:
            dac_value += 1
        elif adc_ext_read > 7000 * self.scale_factor:
            dac_value -= 1