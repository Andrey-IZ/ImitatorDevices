import logging
import threading

__version__ = '1.0.0'
__author__ = 'andrey@2412.net'


class Logger(logging.Logger):
    def __init__(self, name):
        super(Logger, self).__init__(name)
        self.__qt_thread_name = ''
        self.__kw_qt_thread = 'qthreadName'

    @property
    def qthread_name(self):
        return self.__qt_thread_name

    @qthread_name.setter
    def qthread_name(self, value):
        self.__qt_thread_name = value

    def qt_log_off(self):
        self.__qt_thread_name = ''

    def __init_qt_param(self, extra, dict_param):
        thread_name = threading.current_thread().name
        if extra:
            if extra.get(self.__kw_qt_thread):
                return
        else:
            extra = {}
        if self.__qt_thread_name and 'Dummy' in thread_name:  # заменить на qt
            dict_param.update({self.__kw_qt_thread: self.__qt_thread_name})
        else:
            dict_param.update({self.__kw_qt_thread: thread_name})
        return extra

    def _init_extra(self, kwargs):
        dict_param = {}
        extra = kwargs.get('extra')
        extra = self.__init_qt_param(extra, dict_param)

        extra.update(dict_param)
        kwargs['extra'] = extra

    def info(self, msg, *args, **kwargs):
        self._init_extra(kwargs)
        super(Logger, self).info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._init_extra(kwargs)
        super(Logger, self).debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._init_extra(kwargs)
        super(Logger, self).error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._init_extra(kwargs)
        super(Logger, self).warning(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        self._init_extra(kwargs)
        super(Logger, self).critical(msg, *args, **kwargs)

    def system(self, msg, *args, **kwargs):
        self.critical(msg, *args, **kwargs)
