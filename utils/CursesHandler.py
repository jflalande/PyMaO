import logging
import curses
from utils.Colors import Colors

class CursesHandler(logging.Handler):
    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen
    def emit(self, record):
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
                LVL = " ERROR "

            self.screen.addstr(LVL, curses.color_pair(col))
            self.screen.addstr(" | ", curses.color_pair(Colors.WHITE))
            self.screen.addstr(msg + "\n",  curses.color_pair(col))
            self.screen.refresh()
