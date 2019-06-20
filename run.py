from queue import Queue
from threading import Thread
from Producer import createJobs
from Worker import doJob
import time
import logging
import experiment
import importlib
import argparse
import configparser

"""
PARAMETERS
"""
# The experiment to run
targetXP = "XPNative"

NB_WORKERS = 4 # No more workers than devices if using devices !

# If you need devices:
DEVICES = ["CB512DXH1C", "CB512ENX66", "CB512FCYAS", "CB512FEL52","CB512DXGVS"]
# DEVICES = ["CB512DXGVS"]

# =============================================================================


# Adds a very verbose level of logs
DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")

def setup_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("config", type=str,
                        help="config file")

    return parser.parse_args()

def debugv(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws)


logging.Logger.debugv = debugv
log = logging.getLogger("orchestrator")

def generateXP(s, *args, **kwargs):
    # Importing module experiment.s
    full_module_name = "experiment." + s

    # The file gets executed upon import, as expected.
    importlib.import_module(full_module_name)

    # Generating object
    return getattr(getattr(experiment,s), s)(*args, **kwargs)

# Tries to apply colors to logs
def applyColorsToLogs():
    try:
        import coloredlogs

        style = coloredlogs.DEFAULT_LEVEL_STYLES
        style['debugv'] = {'color': 'magenta'}
        coloredlogs.install(
            show_hostname=False, show_name=True,
            logger=log,
            level=DEBUG_LEVELV_NUM,
            fmt='%(asctime)s [%(levelname)8s] %(message)s'
            # Default format:
            # fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s
            #  %(message)s'
        )
    except ImportError:
        log.error("Can't import coloredlogs, logs may not appear correctly.")

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

applyColorsToLogs()

# For debugging purpose:
########################
logSetup("normal")
#logSetup("verbose")
#logSetup("veryverbose")

# Reading args
setup_args()

# Config reading
configfile = ""
config = configparser.ConfigParser(configfile)


workers=[]
t_start = time.time()

malware_queue = Queue()
xpModel = generateXP(targetXP)
xpUsesADevice = xpModel.usesADevice()
if len(DEVICES) < NB_WORKERS and xpUsesADevice:
    log.error("No more workers than number of devices !")
    quit()

producer = Thread(target=createJobs, args=[malware_queue, generateXP(targetXP)])
producer.start()

# Waiting the producer to work first (helps for debugging purpose)
time.sleep(1)

# Creating workers
for i in range(NB_WORKERS):
    deviceserial = None
    if xpUsesADevice:
        deviceserial = DEVICES[i]

    worker = Thread(target=doJob, args=[malware_queue, generateXP(targetXP, deviceserial), i+1])
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

t_end = time.time()
log.info("TIME: " + str(round(t_end - t_start,1)) + " s")
