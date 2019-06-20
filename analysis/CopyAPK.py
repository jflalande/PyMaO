
from analysis.Analysis import Analysis
import logging
import shutil

log = logging.getLogger("orchestrator")


class CopyAPK(Analysis):

    # Sending a specific parameter: the version of Android we want to check against this APK
    def __init__(self, xp_, targetDirectory="/tmp"):
        super().__init__(xp_)
        self.targetDirectory = targetDirectory

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Copying APK.")

        try:
            shutil.copy(jsonanalyses["filename"], self.targetDirectory)
        except OSError:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"status": "failed"})
            return False

        return True

