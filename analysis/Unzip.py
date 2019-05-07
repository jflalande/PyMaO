from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")

"""
Unzip may fail
Errors are captured.
"""

class Unzip(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Unzip analysis.")

        command = "unzip \"" + self.xp.APKBASE + "/" + apkname + ".apk\" -d " + apkname
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        return errcode == 0
