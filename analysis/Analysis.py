import logging

log = logging.getLogger("orchestrator")

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
        raise NotImplementedError("Analysis not implemented")

    def checkTMPFS(self):
        command = "mount | grep tmpfs | grep " + self.xp.TMPFS
        log.debug("Analysis: checking TMPFS with command " + command)
        errcode, res = self.xp.exec_in_subprocess(command)
        if res == "":
            raise Exception("No tmpfs mount detected.")

