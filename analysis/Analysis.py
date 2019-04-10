
from command_subprocessor import exec_in_subprocess

class Analysis:

    # The XP this analysis is part of
    xp = None

    def __init__(self, xp_):
        self.xp = xp_

    def getName(self):
        return __name__

    def run(self, analysis, analysis_name, apkname, jsonanalyses):
        self.checkTMPFS()
        self.analysis(analysis, analysis_name, apkname, jsonanalyses)

    def analysis(self):
        print("Running Apktool analysis.")
        raise NotImplementedError("Analysis not implemented")

    def checkTMPFS(self):
        command = "mount | grep tmpfs | grep " + self.xp.TMPFS
        print("Analysis: executing " + command)
        errcode, res = exec_in_subprocess(command)
        if res == "":
            raise Exception("No tmpfs mount detected.")

