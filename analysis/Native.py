
from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class Native(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Native analysis.")

        command = "grep -r \"static native\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        #jsonanalyses["native_methods"] = res != ""
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"native_methods" : res != ""})
        # This analysis cannot fail
        return True