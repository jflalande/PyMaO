
from analysis.Analysis import Analysis
import logging
import os
from os.path import relpath
import errno

log = logging.getLogger("orchestrator")


class SymlinkAPK(Analysis):

    # Sending a specific parameter: the version of Android we want to check against this APK
    def __init__(self, xp_, targetDirectory="/tmp"):
        super().__init__(xp_)
        self.targetDirectory = targetDirectory

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Symlink APK.")

        relative = relpath(jsonanalyses["filename"], self.targetDirectory)

        try:
            log.debug("Symlink: " + self.targetDirectory + "/" + basename + ".apk" + " => " + relative)
            os.symlink(relative, self.targetDirectory + "/" + basename + ".apk")
        except OSError as e:
            # If the symlink exists, probably it's because of a previous execution and all is fine
            if e.errno != errno.EEXIST:
                log.error("OS Error when doing a symlink " + str(e))
                quit()
            log.warning("Symlink already exists: keeping it, it should be ok.")

        return True

