import math, time, datetime

class Time(object):

    def __init__(self) -> None:
        super().__init__()
        self.time = 0
        self.time_skip = 0

    def get_next_time_in_micro(self, fast=True):
        c_time = math.floor(time.time() * 1000000)
        if c_time <= self.time_skip:
            c_time = self.time_skip + 1
        self.time_skip = c_time
        return c_time

    def get_time_in_micro(self, fast=True):
        return math.floor(time.time() * 1000000)

    def start_measure(self, tag="Main"):
        self.time = time.time()
        date = datetime.date.fromtimestamp(self.time)
        print('{} - START TIME: {}'.format(tag, date.ctime()))

    def stop_measure(self, tag="Main"):
        s_time = time.time()
        date = datetime.date.fromtimestamp(s_time)
        print('{} - STOP TIME: {}, DURATION: {}s'.format(tag, date.ctime(), s_time - self.time))

