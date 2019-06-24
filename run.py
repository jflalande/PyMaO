from queue import Queue
from threading import Thread
from workers.Producer import createJobs
from workers.Worker import doJob
from workers.StatisticsWorker import StatisticsWorker
import time
import logging
import experiment
import importlib
import argparse
import configparser
import curses
from utils.CursesHandler import CursesHandler
import signal
import sys
import ast

def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("config", type=str,
                        help="config file")

    return parser.parse_args()

def generateXP(s, *args, **kwargs):
    # Importing module experiment.s
    full_module_name = "experiment." + s

    # The file gets executed upon import, as expected.
    importlib.import_module(full_module_name)

    # Generating object
    # We pass again the name of the XP as a first parameter s + other parameters
    return getattr(getattr(experiment,s), s)(s, *args, **kwargs)

def debugv(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws)

# Adds a very verbose level of logs
DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")
logging.Logger.debugv = debugv
log = logging.getLogger("orchestrator")

def logSetup(level):
    if level == "veryverbose":
        log.setLevel(DEBUG_LEVELV_NUM)
        log.info("Debug is Very Verbose.")
    elif level == "verbose":
        log.setLevel(logging.DEBUG)
        log.info("Debug is Verbose.")
    elif level == "normal":
        log.setLevel(logging.INFO)
        log.info("Debug is Normal.")
    else:
        log.setLevel(logging.INFO)
        log.warning("Logging level \"{}\" not defined, setting \"normal\" instead"
                    .format(level))

def restoreConsole():
    curses.nocbreak(); stdscr.keypad(0); curses.echo()
    curses.endwin()

# Signal handler for Control+C
# will restore console
def signal_handler(sig, frame):
    restoreConsole()
    print('You pressed Ctrl+C!')
    sys.exit(0)

# Overrinding Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# For debugging purpose:
#applyColorsToLogs()
#logging.basicConfig(format='%(asctime)s [%(levelname)8s] %(message)s')

try:
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak() # No enter needed

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.keypad(True) # Special key

    screen = curses.initscr()
    #screen.nodelay(1) # if used, will cause getch() to not wait.
    maxy, maxx = screen.getmaxyx()
    height = maxy - 2
    width = maxx - 2
    rightcol=30
    log_width=width-rightcol

    screen.border('|', '|', '-', '-', '+', '+', '+', '+')
    win_logs = curses.newwin(height, log_width, 1, 1)
    #win_logs.border('|', '|', '-', '-', '+', '+', '+', '+')

    win_right = curses.newwin(height, rightcol, 1, log_width+1)
    win_right.border('|', '|', '-', '-', '+', '+', '+', '+')
    win_right.scrollok(True)

    curses.setsyx(-1, -1)
    screen.addstr(0, 20, "Malware XP orchestrator", curses.color_pair(4))
    # Refresh: order is important
    screen.refresh()
    win_logs.refresh()
    win_right.refresh()
    win_logs.scrollok(True)

    # Add an handler for the log object for redirecting messages to win
    mh = CursesHandler(win_logs)
    #mh.setFormatter('%(asctime)s [%(levelname)8s] %(message)s')
    log.addHandler(mh)

    # Reading args
    args = vars(setup_args())

    # Config reading
    confparser = configparser.ConfigParser()

    config_file = open(args["config"], "r")
    confparser.read_file(config_file)

    # For debugging purpose:
    logSetup(confparser['general']['debug'])

    # For parameters of the running XP:
    NB_WORKERS = int(confparser['general']['nb_workers'])
    DEVICES = ast.literal_eval(confparser['general']['devices'])
    TMPFS = confparser['general']['tmpfs']

    # Displaying for the user
    log.debugv("ARGS: " + str(args))
    log.info("Reading config file: " + args["config"])
    log.info("General parameters")
    log.info("==================")
    log.info(" - nb_workers: " + str(NB_WORKERS))
    log.info(" - devices: " + str(DEVICES))
    log.info(" - tmpfs: " + str(TMPFS))

    # ==================================================
    log.info("XP parameters")
    log.info("=============")
    targetXP = confparser['xp']['targetXP']
    log.info(" - xp: " + str(targetXP))
    apkbase = confparser['xp']['apkbase']
    log.info(" - apkbase: " + str(apkbase))
    jsonbase = confparser['xp']['jsonbase']
    log.info(" - jsonbase: " + str(jsonbase))
    targetsymlink = confparser['xp']['targetsymlink']
    log.info(" - targetsymlink: " + str(targetsymlink))

    # Starts a thread for stats
    stat_worker = StatisticsWorker(win_right, DEVICES)
    stat_worker.start()

    workers=[]
    t_start = time.time()

    malware_queue = Queue()
    xpModel = generateXP(targetXP, apkbase, jsonbase, targetsymlink, TMPFS)
    xpUsesADevice = xpModel.usesADevice()
    if len(DEVICES) < NB_WORKERS and xpUsesADevice:
        log.error("No more workers than number of devices !")
        quit()

    xp = generateXP(targetXP, apkbase, jsonbase, targetsymlink, TMPFS)
    xp.appendAnalysis()
    producer = Thread(target=createJobs, args=[malware_queue, xp])
    producer.start()

    # Waiting the producer to work first (helps for debugging purpose)
    time.sleep(1)

    # Creating workers
    for i in range(NB_WORKERS):
        deviceserial = None
        if xpUsesADevice:
            deviceserial = DEVICES[i]

        xp = generateXP(targetXP, apkbase, jsonbase, targetsymlink, TMPFS, deviceserial)
        xp.appendAnalysis()
        worker = Thread(target=doJob, args=[malware_queue, xp, i+1])
        worker.start()
        workers.append(worker)

    # Waiting the producer to finish
    producer.join()

    # Adding a fake job in the queue that will be consumed by workers
    for i in range(NB_WORKERS):
        malware_queue.put("--END--")

    # Waiting all workers
    for worker in workers:
        worker.join()

    stat_worker.end = True

    t_end = time.time()
    log.info("TIME: " + str(round(t_end - t_start,1)) + " s")
    log.info("Press q for terminating.")

    #log.warning("This is a warning")
    #log.error("This is an error")

    while True:
        c = screen.getch()
        if c == 113:
           break

        #log.info("Pressed: " + str(c))

    restoreConsole()

except RuntimeError as e:
    restoreConsole()
    print("ERROR")
    print(e)
