from ImitatorDevice.imitator_device_argparse import ImitatorDeviceParams


__author__ = 'Andrey'


class ImitatorSeriaSocketlDeviceParams(ImitatorDeviceParams):
    def __init__(self, path_to_conf, level='INFO'):
        super(ImitatorSeriaSocketlDeviceParams, self).__init__(path_to_conf, level)

    def _init_args(self):
        self._parser.add_argument('-c', '--run-serial-server', dest='run_serial',
                                  action='store_true', help='Run serial server')
        self._parser.add_argument('-s', '--run-socket-server', dest='run_socket',
                                  action='store_true', help='Run socket server [tcp, udp]')
        super(ImitatorSeriaSocketlDeviceParams, self)._init_args()

    def __str__(self):
        if not self._args:
            return 'ImitatorSeriaSocketlDeviceParams(None)'
        param = 'ImitatorSeriaSocketlDeviceParams (path_to_conf={0}, level={1}, run-serial={2}, run-socket={3})'.format(
            self._args.conf_path, self._args.level, self.run_serial, self.run_socket)
        return param


    @property
    def run_serial(self):
        if not self._args:
            return None
        return self._args.run_serial


    @property
    def run_socket(self):
        if not self._args:
            return None
        return self._args.run_socket