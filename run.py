from queue import Queue
from threading import Thread

from utils.Statistics import Statistics
from workers.Producer import createJobs
from workers.Worker import doJob
from workers.StatisticsWorker import StatisticsWorker
from utils.Config import Config
import time
import logging
import experiment
import importlib
import argparse
import curses
from utils.CursesHandler import CursesHandler
import signal
import sys
import ast
import traceback

def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("config", type=str,
                        help="config file")
    parser.add_argument('-v',
                        help='Output information to the standart output (-vv is very verbose)',
                        action="count")

    parser.add_argument("-s", "--simulate_json_write", action="store_true")

    return parser.parse_args()

def generateXP(s, config, deviceserial=None):
    # Importing module experiment.s
    full_module_name = "experiment." + s

    # The file gets executed upon import, as expected.
    importlib.import_module(full_module_name)

    # Generating object
    # We pass again the name of the XP as a first parameter s + other parameters
    return getattr(getattr(experiment,s), s)(config, deviceserial=deviceserial)

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
    curses.curs_set(False)

    curses.start_color()
    curses.init_color(0, 0, 0, 0) # I really want black
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.keypad(True) # Special key

    screen = curses.initscr()
    #screen.nodelay(1) # if used, will cause getch() to not wait.
    maxy, maxx = screen.getmaxyx()
    height = maxy - 2
    width = maxx - 2
    rightcol=34
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



    # Reading args
    args = vars(setup_args())

    # Temporary, just for logging conf parsing.
    log.setLevel(DEBUG_LEVELV_NUM)

    # Config
    config = Config(args)

    # For debugging purpose:
    logSetup(config.debug)

    # Add an handler for the log object for redirecting messages to win
    mh = CursesHandler(win_logs, config.log_trace)
    #mh.setFormatter('%(asctime)s [%(levelname)8s] %(message)s')
    log.addHandler(mh)

    # Displaying for the user
    log.debugv("ARGS: " + str(args))
    log.info("Reading config file: " + args["config"])
    log.info("General parameters")
    log.info("==================")
    log.info(" - nb_workers: " + str(config.nb_workers))
    log.info(" - devices: " + str(config.devices))
    log.info(" - tmpfs: " + str(config.tmpfs))
    log.info(" - sdkhome: " + str(config.sdkhome))
    log.info(" - analysis clean: " + str(config.no_analysis_clean))
    log.info(" - log trace in trace.log: " + str(config.log_trace))
    if config.no_analysis_clean:
        log.warning("Generated files from an analysis will NOT be cleaned!")

    # ==================================================
    log.info("Analysis parameters")
    log.info("===================")
    log.info(" - triggerdroid path: " + str(config.triggerdroid_path))
    log.info(" - heuristics file: " + str(config.heuristicsfile))

    # ==================================================
    log.info("XP parameters")
    log.info("=============")
    log.info(" - xp: " + str(config.targetXP))
    log.info(" - apkbase: " + str(config.apkbase))
    log.info(" - jsonbase: " + str(config.jsonbase))
    log.info(" - targetsymlink: " + str(config.targetsymlink))
    log.info(" - simulate json write: " + str(config.simulate_json_write))

    # Starts a thread for stats
    stat_worker = StatisticsWorker(win_right, config.devices)
    stat_worker.start()

    workers=[]

    Statistics.initTime()
    malware_queue = Queue()
    xpModel = generateXP(config.targetXP, config)
    xpUsesADevice = xpModel.usesADevice()
    if len(config.devices) < config.nb_workers and xpUsesADevice:
        log.error("No more workers than number of devices !")
        quit()

    xp = generateXP(config.targetXP, config)
    xp.appendAnalysis()
    producer = Thread(target=createJobs, args=[malware_queue, xp])
    producer.start()

    # Waiting the producer to work first (helps for debugging purpose)
    time.sleep(1)

    # Creating workers
    for i in range(config.nb_workers):
        deviceserial = None
        if xpUsesADevice:
            deviceserial = config.devices[i]

        xp = generateXP(config.targetXP, config, deviceserial=deviceserial)
        xp.appendAnalysis()
        worker = Thread(target=doJob, args=[malware_queue, xp, i+1])
        worker.start()
        workers.append(worker)

    # Waiting the producer to finish
    producer.join()

    # Adding a fake job in the queue that will be consumed by workers
    for i in range(config.nb_workers):
        malware_queue.put("--END--")

    # Waiting all workers
    for worker in workers:
        worker.join()

    stat_worker.end = True

    t_end = time.time()
    runtime = Statistics.getTime()
    log.info("TIME: " + runtime )
    log.info("Press q for terminating.")

    #log.warning("This is a warning")
    #log.error("This is an error")

    while True:
        c = screen.getch()
        if c == 113:
           break

        #log.info("Pressed: " + str(c))

    restoreConsole()

    # Printing logs
    mh.printLogFromDeque()

except Exception as e:
    # Logging error
    log.error("EXCEPTION catched and forwarded to stdout: " + str(e))

    _, _, tb = sys.exc_info()
    tb_stack = traceback.extract_tb(tb)
    # Printing in logging system
    for line in tb_stack:
        log.error(line)

    # Restoring console
    restoreConsole()
    # Detaching the output from the logging system
    log.removeHandler(mh)

    # Printing logs
    mh.printLogFromDeque()

    # Launching error !
    log.error("EXCEPTION catched and forwarded to stdout: " + str(e))
    raise

