
from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class Native(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Native analysis.")