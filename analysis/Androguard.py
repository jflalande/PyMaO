import logging
from analysis.Analysis import Analysis
from androguard import misc as agmisc


log = logging.getLogger("orchestrator")


class Androguard(Analysis):

    testStaticVariable = 0
    dateArray = {}
    # nb_apk_selected = 0
    max_nb_apk = 5000


    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Analysing APK with Androguard.")

        # Upper bound for the dataset
        # if SelectAPK.nb_apk_selected >= SelectAPK.max_nb_apk:
        #     self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": False})
        #     return True

        # log.info("Do something here Tomas :) ")

        # t_start = time.time()
        # log.debug("Androguard analysis of " + jsonanalyses['filename'])
        a, d, dx = agmisc.AnalyzeAPK(jsonanalyses['filename'])
        # t_end = time.time()
        log.debug("Analysis completed")
        # log.info("Time spent: " + str(round(t_end - t_start, 1)) + " s")

        target_sdk = a.get_target_sdk_version()
        log.debug("Target API: " + str(target_sdk))

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"target_api": target_sdk})

        classes = list(dx.get_classes())

        log.debug("Number of classes found: " + str(len(classes)))

        nb_methods = 0

        classes_name = []
        methods_name = []
        api_methods_name = []

        for c in classes:
            classes_name.append(str(c.name))
            # log.debugv("Class name: " + str(c.name))
            methods = list(c.get_methods())
            nb_methods += len(methods)
            for m in methods:
                # log.info("Method name: " + str(m.name))
                ag_method_name = str(m.method).split(" ")[0]
                is_api_method = m.is_android_api()
                if is_api_method:
                    api_methods_name.append(ag_method_name)
                    # log.debugv("(API Android) Method name: " + str(ag_method_name))
                else:
                    methods_name.append(ag_method_name)
                #     log.debugv("Method name: " + str(ag_method_name))
            # log.info("Class found:" + str(c))

        log.debug("There are " + str(nb_methods) + " methods in the APK")

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"classes": classes_name})
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"methods": methods_name})
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"api_methods": api_methods_name})

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
