import logging
import curses
from utils.Colors import Colors
import collections

class CursesHandler(logging.Handler):
    def __init__(self, screen, log_trace):
        logging.Handler.__init__(self)
        # The screen object of curses
        self.screen = screen
        # A queue used to store last logs messages
        self.dq = collections.deque()
        self.log_trace =log_trace
        if log_trace:
            self.trace = open("trace.log", "w")

    def saveMessageInDeque(self, record):
        self.dq.append(record)
        if len(self.dq) > 500:
            self.dq.popleft()

    def returnMessageFromDeque(self):
        return self.dq

    def printLogFromDeque(self):
        for line in self.dq:
            print(line)

    def logFile(self, line):
        if self.log_trace:
            self.trace.write(line + '\n')

    def emit(self, record):
        # Formatting message
        msg = self.format(record)

        LVL = ""

        if record.levelno == 20:
            col = Colors.WHITE
            LVL = "INFO   "
        elif record.levelno >= 9 and record.levelno <= 10:
            col = Colors.YELLOW
            LVL = "DEBUG  "
        elif record.levelno == 30:
            col = Colors.CYAN
            LVL = "WARNING"
        else:
            col = Colors.RED
            LVL = "ERROR  "

        self.screen.addstr(LVL, curses.color_pair(col))
        self.screen.addstr(" | ", curses.color_pair(Colors.WHITE))
        self.screen.addstr(msg + "\n",  curses.color_pair(col))
        self.screen.refresh()

        # Saving message for further output when ncurses ends
        self.saveMessageInDeque(LVL + "| " + msg)

        # Saving message in the log file
        self.logFile(LVL + "| " + msg)

