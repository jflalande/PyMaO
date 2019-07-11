
import logging

from analysis.Analysis import Analysis
from shutil import copyfile

log = logging.getLogger("orchestrator")


class CopyFile(Analysis):

    # Sending a specific parameter: the version of Android we want to check against this APK
    def __init__(self, xp_, source=None, target=None):
        super().__init__(xp_)
        self.target = target
        self.source = source

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Copying File: ")
        copyfile(self.source, self.target)
        return True
