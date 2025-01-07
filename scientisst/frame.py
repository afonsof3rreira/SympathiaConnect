class Frame:
    """
    ScientISST Device Frame class

    A frame returned by ScientISST.read()

    Attributes:
        seq (int): Frame sequence number (0...15).

            This number is incremented by 1 on each consecutive frame, and it overflows to 0 after 15 (it is a 4-bit number).

            This number can be used to detect if frames were dropped while transmitting data.

        digital (list): Array of digital ports states (False for low level or True for high level).

            On original ScientISST, the array contents are: I1 I2 I3 I4.

            On ScientISST 2, the array contents are: I1 I2 O1 O2.

        a (list): Array of raw analog inputs values of the active channles.

            If all channels are active, `a` will have 8 elements: 6 AIs and 2 AXs.

        mv (list): Array of analog inputs values of the active channles in mV.

            If all channels are active, `mv` will have 8 elements: 6 AIs and 2 AXs.
    """

    digital = [0] * 1
    seq = -1

    def __init__(self, num_channels, EDA_enabled=True):

        self.a = [0] * num_channels
        self.mv = [-1] * num_channels

        if EDA_enabled:
            self.a = [0] * (num_channels - 1)
            self.mv = [-1] * (num_channels - 1)
            self.ax1 = 0
            self.dac = 0

        self.EDA_enabled = EDA_enabled

    def __str__(self):

        if self.mv[0] != -1:
            values = [str(val) for pair in zip(self.a, self.mv) for val in pair]
        else:
            values = map(str, self.a)

        if self.EDA_enabled:
            return "{}\t{}\t{}\t{}\t{}".format(
                self.seq,
                self.digital[0],
                self.ax1,
                self.dac,
                "\t".join(values),
            )

        else:
            return "{}\t{}\t{}".format(
                self.seq,
                self.digital[0],
                "\t".join(values),
            )

    def to_matrix(self):

        if self.EDA_enabled:
            if self.mv[0] != -1:
                return (
                    [self.seq]
                    + self.digital
                    + [self.ax1]
                    + [self.dac]
                    + [val for pair in zip(self.a, self.mv) for val in pair]
                )
            else:
                return [self.seq] + self.digital + [self.ax1] + [self.dac] + self.a

        else:
            if self.mv[0] != -1:
                return (
                    [self.seq]
                    + self.digital
                    + [val for pair in zip(self.a, self.mv) for val in pair]
                )
            else:
                return [self.seq] + self.digital + self.a