import logging
import curses
import time
from threading import Thread
from utils.Statistics import Statistics
from utils.Colors import Colors
from utils.DeviceStatus import DeviceStatus

log = logging.getLogger("orchestrator")


"""
Get a job and launch the missing analyses.

This class is executed in a separate thread.
"""
class StatisticsWorker(Thread):

    def __init__(self, win_right, DEVICES):
        super().__init__()
        self.end = False
        self.win_right = win_right
        self.DEVICES = DEVICES

    def print_right(self, line, x, strip, color, value):
        self.win_right.addstr(line, x, value, curses.color_pair(color))
        remaining_space = strip-len(value)
        if remaining_space > 0:
            self.win_right.addstr(line, x+len(value), " "*remaining_space, curses.color_pair(color))

    def run(self):

        while not self.end:
            line = 1
            total = Statistics.getTotaljobs()
            self.win_right.addstr(line, 2, "Jobs : " + str(total - Statistics.getNbJobs()) +
                                  " / " + str(total) + "\n", curses.color_pair(1))
            line = line + 2

            for device in self.DEVICES:
                line = line + 1
                #self.win_right.addstr(line, 2, device, curses.color_pair(1))
                #self.win_right.addstr(line, 14, str(Statistics.getDeviceStatus(device)), curses.color_pair(1))
                self.print_right(line, 2, len(device), Colors.WHITE, device)
                if Statistics.getDeviceStatus(device) < DeviceStatus.ONLINE:
                    c = Colors.RED
                elif DeviceStatus.ONLINE <= Statistics.getDeviceStatus(device) < DeviceStatus.READY:
                    c = Colors.YELLOW
                else:
                    c = Colors.GREEN
                self.print_right(line, 14, 8, c, str(Statistics.getDeviceStatusString(device)))




            self.win_right.refresh()
            time.sleep(1)