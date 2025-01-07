import copy
import sys
from scientisst.scientisst import AX1, AX2
from sense_src.thread_builder import ThreadBuilder
from datetime import datetime

channels_to_labels = {
    3: 'ACC_Zp',
    1: 'ACC_Xn',
    AX1: 'EDA',
}

class FileWriter(ThreadBuilder):
    def __init__(
        self, filename, address, fs, channels, mv, api_version, firmware_version):
        super().__init__()
        self.filename = filename
        self.mv = mv
        self.channels = channels
        self.metadata = self.__get_metadata(
            address, fs, channels, api_version, firmware_version
        )

    def start(self):
        self.__init_file()
        super().start()

    def stop(self):
        super().stop()
        if self.f:
            self.f.close()

    def thread_method(self, frames):
        self.f.write("\n".join(map(str, frames)) + "\n")

    def __init_file(
        self,
    ):
        self.f = open(self.filename, "w")
        sys.stdout.write("Saving data to {}\n".format(self.filename))

        header = "\t".join(get_header(self.channels))

        self.f.write("#{}\n".format(self.metadata))
        self.f.write("#{}\n".format(header))


    def __get_metadata(self, address, fs, channels, api_version, firmware_version):
        timestamp = datetime.now()

        mode_ = 'Sympathia Sense'

        if mode_ == 'Sympathia Sense':
            metadata = {
                "Device": address,
                "Channels (labels)": [channels_to_labels[ch] for ch in channels],
                "Resolution (bits)": [36, 1, 1, 1, 1] + self.__get_channel_resolutions(),
                "Sampling rate (Hz)": fs,
                "Timestamp (ISO 8601)": timestamp.isoformat(),
                "Channels (hardware)": channels,
                "Firmware version": firmware_version,
                "API version": api_version,
            }
            sorted_metadata = metadata

        else:
            metadata = {
                "API version": api_version,
                "Channels": channels,
                "Channels labels": get_channel_labels(channels, self.mv),
                "Device": address,
                "Firmware version": firmware_version,
                "Header": get_header(channels, self.mv),
                "Resolution (bits)": [4, 1, 1, 1, 1] + self.__get_channel_resolutions(),
                "Sampling rate (Hz)": fs,
                "Timestamp": timestamp.timestamp(),
                "ISO 8601": timestamp.isoformat(),
            }
            if self.mv:
                metadata["Channels indexes raw"] = list(
                    map(lambda x: (x - 1) * 2 + 6, channels)
                )
                metadata["Channels indexes mV"] = list(
                    map(lambda x: (x - 1) * 2 + 7, channels)
                )
            else:
                metadata["Channels indexes"] = list(map(lambda x: x + 5, channels))

            sorted_metadata = {}
            for key in sorted(metadata):
                sorted_metadata[key] = metadata[key]

        return sorted_metadata

    def __get_channel_resolutions(self):
        channel_resolutions = []
        for ch in self.channels:
            if ch == AX1 or ch == AX2:
                channel_resolutions += [24]
            else:
                channel_resolutions += [12]
        return channel_resolutions

    def __get_channel_resolutions_mv(self):
        channel_resolutions = []
        for ch in self.channels:
            if ch == AX1 or ch == AX2:
                channel_resolutions += [0.4]
            else:
                channel_resolutions += [0.8]
        return channel_resolutions


def get_channel_labels(channels, mv):
    channel_labels = []
    for ch in channels:
        if not mv:
            if ch == AX1 or ch == AX2:
                channel_labels += ["AX{}".format(ch)]
            else:
                channel_labels += ["AI{}".format(ch)]
        else:
            if ch == AX1 or ch == AX2:
                channel_labels += ["AX{}_raw".format(ch)]
                channel_labels += ["AX{}_mv".format(ch)]
            else:
                channel_labels += ["AI{}_raw".format(ch)]
                channel_labels += ["AI{}_mv".format(ch)]

    return channel_labels

def get_header(channels):

    if AX1 in channels:

        header = ["NSeq", "O2", "AX1", "DAC"]

        channels_tmp = copy.copy(channels)
        channels_tmp.remove(7)

        for ch in channels_tmp:
            header += [channels_to_labels[ch]]
    else:
        header = ["NSeq", "O2"]

        for ch in channels:
            header += [channels_to_labels[ch]]

    return header

def get_header_sympathia(channels):

    if AX1 in channels:
        header = ["NSeq", "O2", "DAC"]
        for ch in channels:
            header += channels_to_labels[ch]

    else:
        header = ["NSeq", "O2"]
        for ch in channels:
            header += channels_to_labels[ch]

    return header