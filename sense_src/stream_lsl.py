import pylsl
from pylsl import StreamInfo, StreamOutlet, local_clock
import sys

from sense_src.thread_builder import ThreadBuilder


class StreamLSL(ThreadBuilder):
    def __init__(self, channels, fs, address, eda_enable):
        super().__init__()
        if eda_enable:
            no_channels = len(channels) + 1
        else:
            no_channels = len(channels)

        self.info = StreamInfo(
            "ScientISST Sense",
            "RAW",
            no_channels,
            fs,
            "int32",
            address,
        )
        self.eda_enable = eda_enable

    def start(self):
        # make outlet
        self.outlet = StreamOutlet(self.info)

        self.timestamp = local_clock()
        self.previous_index = -1
        self.dt = 1 / self.info.nominal_srate()

        sys.stdout.write("Start LSL stream\n")

        super().start()

    def thread_method(self, frames):
        chunk = []

        for frame in frames:
            analog_section = frame.a

            if self.eda_enable:  # add DAC if EDA is enabled
                dac_value = frame.dac
                analog_section.append(dac_value)

            chunk.append(analog_section)

        num_frames = len(chunk)

        current_index = frames[-1].seq
        lost_frames = current_index - ((self.previous_index + num_frames) & 15)

        if lost_frames > 0:
            self.timestamp = local_clock()
        else:
            self.timestamp += num_frames * self.dt

        self.previous_index = current_index
        self.outlet.push_chunk(chunk, self.timestamp)
