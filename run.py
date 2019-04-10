from queue import Queue
from threading import Thread
from Producer import createJobs
from experiment.XPNative import XPNative
from Worker import doJob
import copy

workers=[]
xp = XPNative() # This XP will be copied for all workers

malware_queue = Queue()
producer = Thread(target=createJobs, args=[malware_queue, xp])
producer.start()

# Creating workers
for i in range(xp.NB_WORKERS):
    worker = Thread(target=doJob, args=[malware_queue, copy.copy(xp)])
    worker.start()
    workers.append(worker)

# Waiting the producer to finish
producer.join()

# Adding a fake job in the queue that will be consumed by workers
for i in range(xp.NB_WORKERS):
    malware_queue.put("--END--")

# Waiting all workers
for worker in workers:
    worker.join()

