import logging
from analysis.Analysis import Analysis
from androguard import misc as agmisc


log = logging.getLogger("orchestrator")


class SelectAPK(Analysis):

    testStaticVariable = 0
    dateArray = {}
    # nb_apk_selected = 0
    max_nb_apk = 5000

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):

        log.debug("Selecting APK.")

        # Upper bound for the dataset
        # if SelectAPK.nb_apk_selected >= SelectAPK.max_nb_apk:
        #     self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": False})
        #     return True

        # log.info("Do something here Tomas :) ")



        # def take_apk(apk):
            # take apk to a list
            # nb_apks_selected += 1
            # dex_date[apk.dex_year] += 1
            # dex_date[total] += 1
            # api_lvl[apk.api_lvl] += 1
            # api_lvl[total] += 1
            # size[apk.size] += 1
            # size[total] += 1

        # def slots_distributed():
            # if

        # Note: How does this type of problem is called? (fill buckets of same size)

        # slots_low = slots_distributed()

        # if not len(slots_low):
            # nb_apks_selected += 1
        # else:
            # if dex_year[apk.dex_year] <= max_nb_apk
                # if api_lvl[apk.api_lvl] <= max_nb_apk
                    # if size[apk.size] <= max_nb_apk
                        # take_apk(apk)

        # SelectAPK.testStaticVariable = SelectAPK.testStaticVariable + 1
        # log.info("For this analysis, the static variable equals " + str(SelectAPK.testStaticVariable))

        # # If the apk is selected
        # # if ...
        # SelectAPK.nb_apk_selected = SelectAPK.nb_apk_selected + 1
        # self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": True})

        # In case there is a big problem
        return True
