import logging
import curses

class CursesHandler(logging.Handler):
    def __init__(self, screen):
        logging.Handler.__init__(self)
        self.screen = screen
    def emit(self, record):
            msg = self.format(record)
            LVL = ""

            if record.levelno == 20:
                col = 1
                LVL = "INFO   "
            elif record.levelno >= 9 and record.levelno <= 10:
                col = 2
                LVL = "DEBUG  "
            elif record.levelno == 30:
                col = 3
                LVL = "WARNING"
            else:
                col = 4
                LVL = " ERROR "
            #msg = str(record.levelno) + " | " + msg
            msg = LVL + " | " + msg
            screen = self.screen
            screen.addstr(msg + "\n",  curses.color_pair(col))
            screen.refresh()
