from enum import IntEnum

""" Helps to encode the device status """
class DeviceStatus(IntEnum):

    WTF = -1 # We cannot send command to the device - something goes wrong
    OFFLINE = 0 # Not seen by adb
    ONLINE = 1 # We see it in adb
    PACKAGE = 2 # the package service is started
    READY = 3 # BOOTCOMPLETED


    def __bool__(self):
        return self.value == DeviceStatus.READY.value
