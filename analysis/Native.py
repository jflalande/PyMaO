
from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class Native(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Native analysis.")

        command = "grep -r \"static native\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"native_methods" : res != ""})

        command = "grep -r \"arm64\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"arm64": res != ""})

        command = "grep -r \"armeabi\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"armeabi": res != ""})

        # This analysis cannot fail
        return True
