from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")

"""
Unzip may fail
Errors are captured.
"""

class Unzip(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running Unzip analysis.")

        command = "unzip \"" + jsonanalyses["filename"] + "\" -d " + basename
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        return errcode == 0
