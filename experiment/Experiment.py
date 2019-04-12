
import logging
import subprocess
import os
import shutil

log = logging.getLogger("orchestrator")

class Experiment:

    APKBASE = ""
    JSONBASE = ""
    # For debugging
    SUBPROCESS_STDERR = os.devnull
    # For release


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
    def exec_in_subprocess(self, cmd, cwd=False, donotcaptureoutput=False):

        log.debugv('Subprocess: ' + str(cmd))
        if cwd:
            log.debugv('Working directory: ' + self.working_directory)
        if donotcaptureoutput:
            log.debugv("Output is not captured for letting the command execute properly.")
        out = ""
        exitcode = -1
        with open(self.SUBPROCESS_STDERR, 'w') as STDERR:
            if not donotcaptureoutput:
                if cwd:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=STDERR, shell=True, cwd=self.working_directory)
                else:
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=STDERR, shell=True)

                with process.stdout: # For closing properly stdout
                    for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                        try:
                            linestr = line.decode('utf-8').rstrip()
                            out = out + line.decode('utf-8')
                            log.debugv("  |" + linestr)
                        except UnicodeDecodeError:
                            log.warning("A string of the output of the cmd " + str(cmd) + " contains an illegal character (not UTF-8): ignoring.")
            else:
                if cwd:
                    process = subprocess.Popen(cmd, cwd=self.working_directory, shell=True, stderr=STDERR)
                else:
                    process = subprocess.Popen(cmd, shell=True, stderr=STDERR)

        # Wait after consuming output (if there is a capture of the output)
        exitcode = process.wait()

        log.debugv("Result of subprocess:")
        log.debugv("Out: " + out)
        log.debugv("Exit code: " + str(exitcode))
        return exitcode, out
