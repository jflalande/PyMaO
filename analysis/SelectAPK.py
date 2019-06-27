import logging
from analysis.Analysis import Analysis

log = logging.getLogger("orchestrator")


class SelectAPK(Analysis):

    testStaticVariable = 0
    dateArray = {}


    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Selecting APK.")

        log.info("Do something here Tomas :) ")







        SelectAPK.testStaticVariable = SelectAPK.testStaticVariable + 1
        log.info("For this analysis, the static variable equals " + str(SelectAPK.testStaticVariable))

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": True})

        # In case there is a big problem
        return True