import threading
import copy
import time
import datetime
from utils.DeviceStatus import DeviceStatus

class Statistics():

    nbjobs = 0
    totaljobs = 0
    lock = threading.Lock()
    device_status = {}
    xp_result = {}
    t_start = 0

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

    @staticmethod
    def recordXPResult(analysis_name, jsonanalysis):
        Statistics.lock.acquire()
        status = jsonanalysis[analysis_name]["status"]
        if analysis_name not in Statistics.xp_result:
            Statistics.xp_result[analysis_name] = {"done": 0, "precond_false": 0, "failed": 0, "total": 0}
        Statistics.xp_result[analysis_name][status] = Statistics.xp_result[analysis_name][status] + 1
        Statistics.xp_result[analysis_name]["total"] = Statistics.xp_result[analysis_name]["total"] + 1
        Statistics.lock.release()

    @staticmethod
    def getXPResult():
        Statistics.lock.acquire()
        xp_result = copy.copy(Statistics.xp_result)
        Statistics.lock.release()
        return xp_result

    @staticmethod
    def initTime():
        Statistics.t_start = time.time()

    @staticmethod
    def getTime():
        duration =  datetime.timedelta(seconds=time.time() - Statistics.t_start)
        return str(duration).split(".")[0]