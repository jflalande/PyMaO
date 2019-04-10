""" Utilities for BranchExplorer. """

import logging
import subprocess

log = logging.getLogger("orchestrator")

'''
This is an attempt to unifiy all subprocess commands
in one function.

The output can go in the very verbose debug log.
For commands that manipulates the output, the output should not be captured. For this purpose the
donotcpatureoutput arguments helps to achieve this.
'''
def exec_in_subprocess(cmd, donotcaptureoutput=False):

    log.debug('Subprocess: ' + str(cmd))
    if donotcaptureoutput:
        log.debug("Output is not captured for letting the command execute properly.")
    out = ""
    exitcode = -1
    if not donotcaptureoutput:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=None, shell=True)
        with process.stdout:
            exitcode = process.wait()  # 0 means success
            for line in iter(process.stdout.readline, b''):  # b'\n'-separated lines
                try:
                    linestr = line.decode('utf-8').rstrip()
                    out = out + line.decode('utf-8')
                    log.debug("  |" + linestr)
                except UnicodeDecodeError:
                    log.warning("A string of the output of the cmd " + str(cmd) + " contains an illegal character (not UTF-8): ignoring.")
    else:
        process = subprocess.Popen(cmd)
        exitcode = process.wait()

    return exitcode, out
