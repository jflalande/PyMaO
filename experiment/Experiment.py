
import logging
import subprocess
import os
import shutil
import time
import threading

log = logging.getLogger("orchestrator")

"""
This class implements all common codes of an experiment.
"""
class Experiment:

    APKBASE = ""
    JSONBASE = ""
    SDKHOME = ""
    deviceserial = None
    worker_nb = -1
    device_local_port = -1

    # For release
    SUBPROCESS_STDERR = os.devnull
    # For debugging
    #
    #SUBPROCESS_STDERR = os.stdout


    # To perform before launching the XP:
    # sudo mount -t tmpfs -o size=512M tmpfs /home/jf/swap/tmpfs/
    #
    # Define this variable, without trailing slash:
    TMPFS="/home/jf/Téléchargements/tmpfs"

    analyses = []
    # Unique identifier of the thread working on this XP
    tid = "NONE"
    working_directory = "NONE"

    ''' By defautl, an XP does not use a device '''
    def usesADevice(self):
        return False

    def setupWorkingDirectory(self):
        log.debugv("Creating working directory " + self.TMPFS + "/" + self.tid)
        try:
            os.mkdir(self.TMPFS + "/" + self.tid)
            self.working_directory = self.TMPFS + "/" + self.tid
        except:
            raise Exception("Error creating directory " + self.TMPFS + "/" + self.tid)

    def cleanWorkingDirectory(self):
        log.debugv("Cleaning TMPFS for pid " + self.tid)
        shutil.rmtree(self.TMPFS + "/" + self.tid)

    def cleanTMPFSDirectory(self):
        log.info("Cleaning TMPFS")
        for the_file in os.listdir(self.TMPFS):
            shutil.rmtree(self.TMPFS + "/" + the_file)

    '''
    This is an attempt to unifiy all subprocess commands
    in one function.
    
    The output can go in the very verbose debug log.
    For commands that manipulates the output, the output should not be captured. For this purpose the
    donotcpatureoutput arguments helps to achieve this.
    '''
    def exec_in_subprocess(self, cmd, donotcaptureoutput=False, cwd=None, shell=True):

        log.debugv('Subprocess: ' + str(cmd))
        if cwd:
            log.debugv('Working directory: ' + self.working_directory)
            cwd = self.working_directory

        if donotcaptureoutput:
            log.debugv("Output is not captured for letting the command execute properly.")
            stdout = None
            stderr = None
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT

        # Execute the command
        log.debugv("Executing: " + str(cmd) + " cwd=" + str(cwd) + " shell=" + str(shell) + " stdout=" + str(stdout))
        process = subprocess.Popen(cmd, cwd=cwd, shell=shell, stdout=stdout, stderr=stderr)

        # Consume output
        out = ""
        if not donotcaptureoutput:
            with process.stdout:  # For closing properly stdout
                for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                    try:
                        linestr = line.decode('utf-8').rstrip()
                        out = out + line.decode('utf-8')
                        log.debugv("  |" + linestr)
                    except UnicodeDecodeError:
                        log.warning("A string of the output of the cmd " + str(
                            cmd) + " contains an illegal character (not UTF-8): ignoring.")

        # Wait after consuming output (if there is a capture of the output)
        exitcode = process.wait()

        log.debugv("Result of subprocess:")
        log.debugv("Out: " + out)
        log.debugv("Exit code: " + str(exitcode))
        return exitcode, out


    """
    Sends command to the smartphone using ADB.
    """
    def adb_send_command(self, command, donotcaptureoutput=False):
        """ Send a command to this device (by default through ADB). """
        tool_command = [self.SDKHOME + "/platform-tools/adb", "-s", self.deviceserial] + command
        log.debug("Sending command: " + str(tool_command))
        exitcode, out = self.exec_in_subprocess(tool_command, donotcaptureoutput=donotcaptureoutput, shell=False)
        return exitcode, out


    """ One time check a device """
    def setupDeviceUsingAdb(self):
        log.info("Checking and preparing device " + str(self.deviceserial))
        if self.deviceserial == None:
            return
        exitcode, res = self.adb_send_command(["devices"])
        for line in res.split('\n'):
            if line.startswith(self.deviceserial):
                log.info(" - found")
                break
        # We cannot find the device
        if not line.startswith(self.deviceserial):
            log.error("No device " + self.deviceserial + " detecting using adb.")
            quit()

        # Killing previous remaining process (if any)
        self.cleanDeviceUsingAdb()

        # Installing the watchdog
        log.info(" - pushing watchdog.arm64")
        _,res = self.adb_send_command(["push", "watchdog.arm64", "/data/local/tmp/watchdog.arm64"])
        if not res.startswith("watchdog.arm64: 1 file pushed"):
            log.error("Error pushing watchdog.arm64")
            quit()

        # Forwaring ports
        self.device_local_port = 4446 + self.worker_nb
        log.info(" - redirecting local port " + str(self.device_local_port) + " to smartphone port 4446")
        _,res = self.adb_send_command(["forward", "tcp:" + str(self.device_local_port), "tcp:4446"])

        # Launching the watchdog
        log.info(" - activating watchdog.arm64")
        self.adb_send_command(["shell", "/data/local/tmp/watchdog.arm64", "4446"])

    """ Kill the watchdog.arm64 """
    def cleanDeviceUsingAdb(self):

        log.info(" - killing previous watchdog.arm64")
        self.adb_send_command(["shell", "pkill", "watchdog.arm64"])

    """ Clean /data/local/tmp/traced_uid """
    def cleanOatSInsideTracing(self):

        log.warning("Cleaning oat's inside tracing file because we are booting ?!")
        self.adb_send_command(["shell", "rm", "/data/local/tmp/traced_uid"])

    """ Checks that the  device is ok
        Multiple tests are done because the device may reboot unexpectivelly
        - "adb device" command should returns "device" (and not offline) 
        - service package should be ready
    """
    def check_device_online(self):

        log.debug("Checking device online/offline " + str(self.deviceserial))
        device_detected = False
        for i in range(2):
            exitcode, res = self.adb_send_command(["devices"])
            secondline = res.split('\n')[1] # Second line should contain "uid device"
            if self.deviceserial in secondline and "device" in secondline:
                device_detected = True
                break
            # Wow ! The device is gone ??? Check again one time more...
            log.warning("WTF? device offline ? Waiting 10.")
            time.sleep(2)
        if not device_detected:
            return False


        log.debug("Checking package service " + str(self.deviceserial))
        detected_package = False
        for i in range(6):
            exitcode, res = self.adb_send_command(["shell", "service", "check", "package"])
            if "Service package: found" in res:
                detected_package = True
                break
            # Wow ! The device is gone ??? Check again one time more...

            self.cleanOatSInsideTracing()
            log.warning("WTF? service package not there ? Waiting 10.")
            time.sleep(10)
        if not detected_package:
            return False

        log.debug("Checking boot completed " + str(self.deviceserial))
        detected_boot = False
        for i in range(10):
            exitcode, res = self.adb_send_command(["shell", "getprop", "dev.bootcomplete"])
            if "1" in res:
                detected_boot = True
                break
            # Wow ! The device is gone ??? Check again one time more...
            log.warning("WTF? service package not there ? Waiting 10.")
            time.sleep(10)
        if not detected_boot:
            return False

        # All is going well :)
        return True

    def check_device_online_or_wait_reboot(self):

        if self.check_device_online():
            # Updating watchdog
            # echo -n "ALIVE" | nc localhost 444x
            self.exec_in_subprocess("echo -n 'ALIVE' | nc localhost " + str(self.device_local_port), shell=True)
            return

        log.warning("Device " + self.deviceserial + " seems offline !")
        log.warning("Waiting the reboot initiated by watchdog.arm64")
        print('\a') # BEEP

        self.cleanOatSInsideTracing()

        log.debug("Sleeping 60s...")
        time.sleep(60)
        log.warning("The reboot should have occurred")
        log.warning("Waiting 30s for the boot process makes adb appearing...")
        time.sleep(30)

        while not self.check_device_online():
            log.warning("Checking device via adb...")
            time.sleep(5)
        log.warning("Waiting an additional 70s to have the welcome screen...")
        time.sleep(70)

        if not self.check_device_online():
            log.error("The reboot process FAILED :-(")
            quit()

        log.warning("Rearming the watchdog...")
        self.setupDeviceUsingAdb()

        log.warning("It should be ok now.")

    def wake_up_and_unlock_device(self):

        self.check_device_online()

        log.debug("Waking up screen")
        # https://stackoverflow.com/questions/35275828/is-there-a-way-to-check-if-android-device-screen-is-locked-via-adb
        # adb shell service call power 12
        # Result: Parcel(00000000 00000001   '........')
        exitcode, res = self.adb_send_command(["shell", "service", "call", "power", "12"])
        while res != "Result: Parcel(00000000 00000001   '........')\n":
            self.adb_send_command(["shell", "input", "keyevent", "26"])
            time.sleep(0.5)
            exitcode, res = self.adb_send_command(["shell", "service", "call", "power", "12"])

        # https://stackoverflow.com/questions/29072501/how-to-unlock-android-phone-through-adb
        self.adb_send_command(["shell", "input", "keyevent", "82"])

