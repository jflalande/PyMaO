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
        ret =  self.analysis(analysis, analysis_name, apkname, jsonanalyses)

        # Update status of this analysis
        if ret:
            self.updateJsonAnalyses(analysis_name, jsonanalyses,{"status": "done"})
        else:
            log.warning("Analysis failed.")

        return ret

    def analysis(self):
        raise NotImplementedError("Analysis not implemented")

    def checkTMPFS(self):
        command = "mount | grep tmpfs | grep " + self.xp.TMPFS
        log.debug("Analysis: checking TMPFS with command " + command)
        errcode, res = self.xp.exec_in_subprocess(command)
        if res == "":
            raise Exception("No tmpfs mount detected.")

    def updateJsonAnalyses(self, analysis_name, jsonanalyses, newdata):
        log.debug("Updating JSON with result: " + str(newdata))
        if analysis_name in jsonanalyses:
            info_analysis = jsonanalyses[analysis_name]
            info_analysis.update(newdata)
        else:
            jsonanalyses[analysis_name] = newdata