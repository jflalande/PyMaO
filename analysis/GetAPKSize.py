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

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GetAPKSize analysis.")

        # file_path = self.xp.TMPFS + "/" + self.xp.tid  + "/" + apkname

        # -b : print size in octets (kyloctets by default)
        # -L : dereferenc the symbolic link, get the size of the reference
        command = "du -bL \"" + jsonanalyses["filename"]

        log.debug("The command is "+command)

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        log.debug("Got: " + str(res))

        size = res.strip().split()[0]

        log.debug("True size: " + str(size))

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"size": size})

        return 1
