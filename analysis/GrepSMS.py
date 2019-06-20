
from analysis.Analysis import Analysis
import logging
import os

log = logging.getLogger("orchestrator")


class GrepSMS(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GrepSMS analysis.")

        command = "grep -Er \"\.*SMS.* \" ."
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        for line in res.split('\n'):
            print(line)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"Search for string SMS" : res })


        # This analysis cannot fail
        return True
