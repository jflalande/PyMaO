
import logging
import subprocess
import os
import shutil
import time

log = logging.getLogger("orchestrator")

"""
This class implements all common codes of an experiment.
"""
class Experiment:

    APKBASE = ""
    JSONBASE = ""
    SDKHOME = ""
    deviceserial = None
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

    ''' By defautl, an XP does not use a drvice '''
    def usesADevice(self):
        return False

    def setupDeviceUsingAdb(self):
        if self.deviceserial == None:
            return
        exitcode, res = self.adb_send_command(["devices"])
        for line in res.split('\n'):
            if line.startswith(self.deviceserial):
                return
        log.error("No device " + self.deviceserial + " detecting using adb.")
        quit()

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

    def wake_up_and_unlock_device(self):
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

