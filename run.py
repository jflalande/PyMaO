from queue import Queue
from threading import Thread
from Producer import createJobs
from experiment.XPNative import XPNative
from Worker import doJob
import time
import logging


# Adds a very verbose level of logs
DEBUG_LEVELV_NUM = 9
logging.addLevelName(DEBUG_LEVELV_NUM, "DEBUGV")


def debugv(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    if self.isEnabledFor(DEBUG_LEVELV_NUM):
        self._log(DEBUG_LEVELV_NUM, message, args, **kws)


logging.Logger.debugv = debugv
log = logging.getLogger("orchestrator")


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

#logging.basicConfig(stream=sys.stdout)


"""
PARAMETERS
"""
NB_WORKERS = 3

#logSetup("verbose")
#logSetup("veryverbose")
logSetup("info")

workers=[]
t_start = time.time()

malware_queue = Queue()
producer = Thread(target=createJobs, args=[malware_queue, XPNative()])
producer.start()

# Creating workers
for i in range(NB_WORKERS):
    worker = Thread(target=doJob, args=[malware_queue, XPNative()])
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