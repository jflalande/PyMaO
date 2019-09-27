import threading

class PrintCursesScreen:

    lock = threading.Lock()

    @staticmethod
    def addstr(win, string, color):
        PrintCursesScreen.lock.acquire()
        win.addstr(string, color)
        PrintCursesScreen.lock.release()

    @staticmethod
    def addstrXY(win, y, x, string, color):
        PrintCursesScreen.lock.acquire()
        win.addstr(y, x, string, color)
        PrintCursesScreen.lock.release()

    @staticmethod
    def refresh(win):
        PrintCursesScreen.lock.acquire()
        win.refresh()
        PrintCursesScreen.lock.release()
