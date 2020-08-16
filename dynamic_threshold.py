import audioop
from configparser import ConfigParser

import pyaudio

config = ConfigParser()
config.read('audio_config.ini')

FORMAT = getattr(pyaudio, config.get('config', 'FORMAT'))
THRESHOLD = config.getint('config', 'THRESHOLD')
CHUNK = config.getint('config', 'CHUNK_SIZE')
CHANNELS = config.getint('config', 'CHANNELS')
S_RATE = config.getint('config', 'SAMPLE_RATE')
S_WIDTH = config.getint('config', 'SAMPLE_WIDTH')


class DynamicThreshold():
    def __init__(self):
        self.energy_threshold = THRESHOLD
        self.CHUNK = CHUNK
        self.SAMPLE_RATE = S_RATE
        self.SAMPLE_WIDTH = S_WIDTH
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 0.10

    def adjust_for_ambient_noise(self, source, duration=1):
        """
        Implementation by Anthony Zhang (https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py#L547)

        Adjusts the energy threshold dynamically using audio from ``source`` to account for ambient noises.
        Intended to calibrate the energy threshold with the ambient energy level.
        Should be used on periods of audio without speech - will stop early if any speech is detected.
        The ``duration`` parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning.
        This value should be at least 0.5 in order to get a representative sample of the ambient noise.
        """

        seconds_per_buffer = self.CHUNK / self.SAMPLE_RATE
        elapsed_time = 0

        # adjust energy threshold until a phrase starts
        while True:
            elapsed_time += seconds_per_buffer
            if elapsed_time > duration:
                break
            buffer = source.read(self.CHUNK)
            # energy of the audio signal
            energy = audioop.rms(buffer, self.SAMPLE_WIDTH)

            # dynamically adjust the energy threshold using asymmetric weighted average
            # account for different chunk sizes and rates
            damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer
            target_energy = energy * self.dynamic_energy_ratio
            self.energy_threshold = self.energy_threshold * \
                damping + target_energy * (1 - damping)

        return self.energy_threshold


p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=S_RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

dt = DynamicThreshold()
NEW_THRESHOLD = dt.adjust_for_ambient_noise(stream, duration=5)

config.set('config', 'THRESHOLD', str(int(NEW_THRESHOLD)))
config.write(open("audio_config.ini", "w"))
