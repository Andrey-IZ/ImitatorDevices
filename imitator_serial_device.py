__author__ = 'Andrey'

from ImitatorDevice.imitator_device_argparse import ImitatorDeviceParams


class ImitatorSerialDeviceParams(ImitatorDeviceParams):
    def __init__(self, path_to_conf, level='INFO'):
        super(ImitatorSerialDeviceParams, self).__init__(path_to_conf, level)
