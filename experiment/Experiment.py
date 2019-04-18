
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
    devicesesrial = "XXX"
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


    '''
    This is an attempt to unifiy all subprocess commands
    in one function.
    
    The output can go in the very verbose debug log.
    For commands that manipulates the output, the output should not be captured. For this purpose the
    donotcpatureoutput arguments helps to achieve this.
    '''
    def exec_in_subprocess(self, cmd, cwd=False, donotcaptureoutput=False, shell=True):

        log.debugv('Subprocess: ' + str(cmd))
        if cwd:
            log.debugv('Working directory: ' + self.working_directory)
        if donotcaptureoutput:
            log.debugv("Output is not captured for letting the command execute properly.")
        out = ""
        exitcode = -1
        with open(self.SUBPROCESS_STDERR, 'w') as STDERR:
            if not donotcaptureoutput:
                log.debugv("Output is captured and redirected to debugv and returned.")
                if cwd:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=STDERR, shell=shell, cwd=self.working_directory)
                else:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,  shell=shell)

                with process.stdout: # For closing properly stdout
                    for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                        try:
                            linestr = line.decode('utf-8').rstrip()
                            out = out + line.decode('utf-8')
                            log.debugv("  |" + linestr)
                        except UnicodeDecodeError:
                            log.warning("A string of the output of the cmd " + str(cmd) + " contains an illegal character (not UTF-8): ignoring.")
            else:
                log.debugv("Output is NOT captured (you should see it) and lost.")
                if cwd:
                    process = subprocess.Popen(cmd, cwd=self.working_directory, shell=shell, stderr=STDERR)
                else:
                    process = subprocess.Popen(cmd, shell=shell, stderr=STDERR)

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
        tool_command = [self.SDKHOME + "/platform-tools/adb", "-s", self.devicesesrial] + command
        log.debug("Sending command: " + str(tool_command))
        exitcode, out = self.exec_in_subprocess(tool_command, donotcaptureoutput, shell=False)
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

        self.adb_send_command(["shell", "input", "keyevent", "82"])

