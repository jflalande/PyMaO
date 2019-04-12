
from analysis.Analysis import Analysis
import logging
import os
from os.path import relpath

log = logging.getLogger("orchestrator")


class SymlinkAPK(Analysis):

    # Sending a specific parameter: the version of Android we want to check against this APK
    def __init__(self, xp_, targetDirectory="/tmp"):
        super().__init__(xp_)
        self.targetDirectory = targetDirectory

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Symlink APK.")

        relative = relpath(self.xp.APKBASE + "/" + apkname + ".apk", self.targetDirectory)

        try:
            log.debug("Symlink: " + self.targetDirectory + "/" + apkname + ".apk" + " => " + relative)
            os.symlink(relative, self.targetDirectory + "/" + apkname + ".apk")
        except OSError:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"status": "failed"})
            return False

        return True

