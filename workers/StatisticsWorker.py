import logging
import curses
import time
from threading import Thread
from utils.Statistics import Statistics
from utils.Colors import Colors
from utils.DeviceStatus import DeviceStatus
from utils.PrintCursesScreen import PrintCursesScreen

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

    # Print in the right box
    # y is y position
    # x is the x position
    # stip is the max number of characters to print and that deletes holds displayed strings
    # color is the color to use
    # value is the string to print
    def print_right(self, y, x, strip, color, value):
        #self.win_right.addstr(y, x, value, curses.color_pair(color))
        PrintCursesScreen.addstrXY(self.win_right, y, x, value, curses.color_pair(color))
        remaining_space = strip-len(value)
        if remaining_space > 0:
            #self.win_right.addstr(y, x + len(value), " " * remaining_space, curses.color_pair(color))
            PrintCursesScreen.addstrXY(self.win_right, y, x + len(value), " " * remaining_space, curses.color_pair(color))
            return strip
        return len(value)

    def run(self):

        while not self.end:
            time.sleep(0.1)
            y = 1
            total = Statistics.getTotaljobs()
            self.print_right(y, 2, 20, Colors.WHITE, "Jobs : " + str(total - Statistics.getNbJobs()) + " / " + str(total) + "\n")

            # Devices
            y = y + 2
            self.print_right(y, 2, 20, Colors.WHITE, "Devices:")
            y = y + 1
            self.print_right(y, 2, 20, Colors.WHITE, "--------")
            y = y + 1
            for device in self.DEVICES:
                self.print_right(y, 2, len(device), Colors.WHITE, device)
                if Statistics.getDeviceStatus(device) < DeviceStatus.ONLINE:
                    c = Colors.RED
                elif DeviceStatus.ONLINE <= Statistics.getDeviceStatus(device) < DeviceStatus.READY:
                    c = Colors.YELLOW
                else:
                    c = Colors.GREEN
                self.print_right(y, 14, 8, c, str(Statistics.getDeviceStatusString(device)))
                y = y + 1

            # XP Status
            y = y + 2
            self.print_right(y, 2, 20, Colors.WHITE, "XP Status:")
            y = y + 1
            self.print_right(y, 2, 20, Colors.WHITE, "----------")
            y = y + 1
            self.print_right(y, 2, 0, Colors.GREEN, "DONE ")
            self.print_right(y, 7, 0, Colors.YELLOW, "PREC ")
            self.print_right(y, 12, 0, Colors.RED, "FAIL ")
            self.print_right(y, 17, 0, Colors.WHITE, "TOTAL ")
            y = y + 1

            xp_result = Statistics.getXPResult()
            for analysis in xp_result:
                self.print_right(y, 2, 0, Colors.WHITE, analysis + ": ")
                y = y + 1
                l = self.print_right(y, 2, 0, Colors.GREEN, str(xp_result[analysis]["done"]))
                l = l + self.print_right(y, 2 + l, 0, Colors.WHITE, " / ")
                l = l + self.print_right(y, 2 + l, 0, Colors.YELLOW, str(xp_result[analysis]["precond_false"]))
                l = l + self.print_right(y, 2 + l, 0, Colors.WHITE, " / ")
                l = l + self.print_right(y, 2 + l, 0, Colors.RED, str(xp_result[analysis]["failed"]))
                l = l + self.print_right(y, 2 + l, 0, Colors.WHITE, " / ")
                l = l + self.print_right(y, 2 + l, 0, Colors.WHITE, str(xp_result[analysis]["total"]))
                y = y + 1

            y = y + 1
            self.print_right(y, 2, 20, Colors.WHITE, "Time: " + Statistics.getTime())


            PrintCursesScreen.refresh(self.win_right)
