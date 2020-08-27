import os
from configparser import ConfigParser

import pyaudio


audio_confs = ConfigParser()
audio_confs.read(os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'audio_config.ini'))

FORMAT = getattr(pyaudio, audio_confs.get('config', 'FORMAT'))
THRESHOLD = audio_confs.getint('config', 'THRESHOLD')
CHUNK = audio_confs.getint('config', 'CHUNK_SIZE')
CHANNELS = audio_confs.getint('config', 'CHANNELS')
S_RATE = audio_confs.getint('config', 'SAMPLE_RATE')
S_WIDTH = audio_confs.getint('config', 'SAMPLE_WIDTH')