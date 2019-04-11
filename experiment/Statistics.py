import threading

class Statistics():

    nbjobs = 0
    lock = threading.Lock()

    @staticmethod
    def incNbJobs():
        Statistics.lock.acquire()
        Statistics.nbjobs = Statistics.nbjobs + 1
        Statistics.lock.release()

    @staticmethod
    def decNbJobs():
        Statistics.lock.acquire()
        Statistics.nbjobs = Statistics.nbjobs - 1
        Statistics.lock.release()

    @staticmethod
    def getNbJobs():
        Statistics.lock.acquire()
        nb = Statistics.nbjobs
        Statistics.lock.release()
        return nb

