
from command_subprocessor import exec_in_subprocess

class Experiment:

    APKBASE = ""
    JSONBASE = ""
    NB_WORKERS = 0

    # To perform before launching the XP:
    # sudo mount -t tmpfs -o size=512M tmpfs /home/jf/swap/tmpfs/
    #
    # Define this variable, without trailing slash:
    TMPFS="/home/jf/Téléchargements/tmpfs"

    analyses = []
    # Unique identifier of the thread working on this XP
    tid = "NONE"

    def setupWorkingDirectory(self):
        command = "mkdir " + self.TMPFS + "/" + self.tid
        errcode, res = exec_in_subprocess(command)
        print("ERrc" + str(errcode))
        if errcode != 0:
            raise Exception("Experiment: Error: " + command)

    def cleanWorkingDirectory(self):
        command = "rm -Rf " + self.TMPFS + "/" + self.tid
        errcode, res = exec_in_subprocess(command)
        if errcode != 0:
            raise Exception("Experiment: Error: " + command)

