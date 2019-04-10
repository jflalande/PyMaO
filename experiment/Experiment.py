
import logging
import subprocess

log = logging.getLogger("orchestrator")

class Experiment:

    APKBASE = ""
    JSONBASE = ""

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
        command = "mkdir " + self.TMPFS + "/" + self.tid
        log.debug("Creating working directory " + command)
        errcode, res = self.exec_in_subprocess(command)
        if errcode != 0:
            raise Exception("Experiment: Error: " + command)
        self.working_directory = self.TMPFS + "/" + self.tid


    def cleanWorkingDirectory(self):
        command = "rm -Rf " + self.TMPFS + "/" + self.tid
        errcode, res = self.exec_in_subprocess(command)
        if errcode != 0:
            raise Exception("Experiment: Error: " + command)

    '''
    This is an attempt to unifiy all subprocess commands
    in one function.
    
    The output can go in the very verbose debug log.
    For commands that manipulates the output, the output should not be captured. For this purpose the
    donotcpatureoutput arguments helps to achieve this.
    '''
    def exec_in_subprocess(self, cmd, cwd=False, donotcaptureoutput=False):

        log.debugv('Subprocess: ' + str(cmd))
        if cwd:
            log.debugv('Working directory: ' + self.working_directory)
        if donotcaptureoutput:
            log.debugv("Output is not captured for letting the command execute properly.")
        out = ""
        exitcode = -1
        if not donotcaptureoutput:
            if cwd:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True,
                                           cwd=self.working_directory)
            else:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)

            with process.stdout:
                exitcode = process.wait()  # 0 means success
                for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                    try:
                        linestr = line.decode('utf-8').rstrip()
                        out = out + line.decode('utf-8')
                        log.debugv("  |" + linestr)
                    except UnicodeDecodeError:
                        log.warning("A string of the output of the cmd " + str(cmd) + " contains an illegal character (not UTF-8): ignoring.")
        else:
            if cwd:
                process = subprocess.Popen(cmd, cwd=self.working_directory)
            else:
                process = subprocess.Popen(cmd)

            exitcode = process.wait()

        log.debugv("Result of subprocess:")
        log.debugv("Out: " + out)
        log.debugv("Exit code: " + str(exitcode))
        return exitcode, out
