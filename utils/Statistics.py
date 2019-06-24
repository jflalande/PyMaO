import threading
from utils.DeviceStatus import DeviceStatus

class Statistics():

    nbjobs = 0
    totaljobs = 0
    lock = threading.Lock()
    device_status = {}

    @staticmethod
    def incNbJobs():
        Statistics.lock.acquire()
        Statistics.totaljobs = Statistics.totaljobs + 1
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

    @staticmethod
    def getTotaljobs():
        Statistics.lock.acquire()
        nb = Statistics.totaljobs
        Statistics.lock.release()
        return nb

    @staticmethod
    def publishDeviceStatus(device, status):
        Statistics.lock.acquire()
        Statistics.device_status[device] = status
        Statistics.lock.release()

    @staticmethod
    def getDeviceStatusString(device):
        Statistics.lock.acquire()
        if device in Statistics.device_status:
            status = str(Statistics.device_status[device]).split('.')[1]
        else:
            status = "OFFLINE"
        Statistics.lock.release()
        return status

    @staticmethod
    def getDeviceStatus(device):
        Statistics.lock.acquire()
        if device in Statistics.device_status:
            status = Statistics.device_status[device]
        else:
            status = DeviceStatus.OFFLINE
        Statistics.lock.release()
        return status
