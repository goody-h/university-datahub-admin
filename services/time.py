import math, time, datetime

class Time(object):

    def __init__(self) -> None:
        super().__init__()
        self.time = 0

    def get_time_in_sec(self, fast=True):
        return math.floor(time.time())

    def start_measure(self, tag="Main"):
        self.time = time.time()
        date = datetime.date.fromtimestamp(self.time)
        print('{} - START TIME: {}'.format(tag, date.ctime()))

    def stop_measure(self, tag="Main"):
        s_time = time.time()
        date = datetime.date.fromtimestamp(s_time)
        print('{} - STOP TIME: {}, DURATION: {}s'.format(tag, date.ctime(), s_time - self.time))

