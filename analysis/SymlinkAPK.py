
from analysis.Analysis import Analysis
import logging
import os
from os.path import relpath
import errno

log = logging.getLogger("orchestrator")


class SymlinkAPK(Analysis):

    # Sending a specific parameter: the target directory where to make a symlink
    def __init__(self, xp_, targetDirectory=None):
        super().__init__(xp_)
        # By default, use the parameter targetsymlink that comes from the config file
        self.targetDirectory = targetDirectory

    def getTargetDirectory(self, jsonanalyses):
        if self.targetDirectory == None:
            return self.xp.config.getTargetsymlink(jsonanalyses["filename"])
        else:
            return self.targetDirectory

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Symlink APK.")

        relative = relpath(jsonanalyses["filename"], self.getTargetDirectory(jsonanalyses))

        try:
            log.debug("Symlink: " + self.getTargetDirectory(jsonanalyses) + "/" + basename + ".apk" + " => " + relative)
            os.symlink(relative, self.getTargetDirectory(jsonanalyses) + "/" + basename + ".apk")
        except OSError as e:
            # If the symlink exists, probably it's because of a previous execution and all is fine
            if e.errno != errno.EEXIST:
                log.error("OS Error when doing a symlink " + str(e))
                quit()
            log.warning("Symlink already exists: keeping it, it should be ok.")

        return True

