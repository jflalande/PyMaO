from analysis.Analysis import Analysis
import logging
import os
import time
import datetime

log = logging.getLogger("orchestrator")

"""
GetAPKSize may fail
Errors are captured.
"""

class GetAPKSize(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running GetAPKSize analysis.")

        # file_path = self.xp.TMPFS + "/" + self.xp.tid  + "/" + apkname

        command = "du -b \"" + self.xp.APKBASE + "/" + apkname + ".apk\""

        log.debug("The command is "+command)

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        log.debug("Got: " + str(res))

        size = res.strip().split()[0]

        log.debug("True size: " + str(size))

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"size": size})

        return 1