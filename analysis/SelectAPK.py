import logging
from analysis.Analysis import Analysis

log = logging.getLogger("orchestrator")


class SelectAPK(Analysis):

    testStaticVariable = 0
    dateArray = {}
    nb_apk_selected = 0


    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Selecting APK.")

        # Upper bound for the dataset
        if SelectAPK.nb_apk_selected >= 1000:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": False})
            return True

        log.info("Do something here Tomas :) ")







        SelectAPK.testStaticVariable = SelectAPK.testStaticVariable + 1
        log.info("For this analysis, the static variable equals " + str(SelectAPK.testStaticVariable))

        # If the apk is selected
        # if ...
        SelectAPK.nb_apk_selected = SelectAPK.nb_apk_selected + 1
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": True})

        # In case there is a big problem
        return True