import logging
from sys import platform

log = logging.getLogger("orchestrator")

class Analysis:

    # The XP this analysis is part of
    xp = None

    def __init__(self, xp_):
        self.xp = xp_

    def getName(self):
        return __name__

    def dependencies(self):
        return []

    def run(self, analysis, analysis_name, basename, jsonanalyses):
        self.checkTMPFS()
        ret =  self.analysis(analysis, analysis_name, basename, jsonanalyses)

        # Update status of this analysis
        if ret:
            self.updateJsonAnalyses(analysis_name, jsonanalyses,{"status": "done"})
        else:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"status": "failed"})
            log.warning("Analysis " + analysis_name + " failed (" + basename + ")")

        return ret

    def analysis(self):
        raise NotImplementedError("Analysis not implemented")

    def checkTMPFS(self):
        log.debug("You are running on "+platform)
        if platform == 'linux' or platform == 'Linux':
            command = "mount | grep '^tmpfs' | grep " + self.xp.TMPFS
        elif platform == 'darwin' :
            command = "mount | grep '(hfs'" # + self.xp.TMPFS
        else :
            log.error ("Your platform seems to be unknown ...")
            quit()
        log.debugv("Analysis: checking TMPFS with command " + command)
        errcode, res = self.xp.exec_in_subprocess(command)
        if res == "":
            log.error("No tmpfs mount detected.")
            log.error("Suggestion: sudo mount -t tmpfs -o size=1G tmpfs " + self.xp.TMPFS)
            quit()

    def updateJsonAnalyses(self, analysis_name, jsonanalyses, newdata):
        log.debug("Updating JSON with result: " + str(newdata))
        if analysis_name in jsonanalyses:
            info_analysis = jsonanalyses[analysis_name]
            info_analysis.update(newdata)
        else:
            jsonanalyses[analysis_name] = newdata
