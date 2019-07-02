import logging
from analysis.Analysis import Analysis
from androguard import misc as agmisc
# from androguard.core.bytecodes import axml
# import zipfile
import re

# Pretty print XML
# import lxml.etree as etree
# myxml = etree.tostring(a.get_android_manifest_xml(), pretty_print=True).decode()
# print(myxml)

# print(etree.tostring(str(a.get_android_manifest_axml().get_xml(), pretty_print=True).decode())
log = logging.getLogger("orchestrator")



class Androguard(Analysis):

    testStaticVariable = 0
    dateArray = {}
    # nb_apk_selected = 0
    max_nb_apk = 5000


    def analysis(self, analysis, analysis_name, basename, jsonanalyses):

        log.debug("Analysing APK with Androguard. ")

        # Variables

        nb_methods = 0

        classes_name = []
        methods_name = []
        api_methods_name = []

        intent_filters = {
            'activity': {},
            'activity-alias': {},
            'service': {},
            'receiver': {}
        }

        # Upper bound for the dataset
        # if SelectAPK.nb_apk_selected >= SelectAPK.max_nb_apk:
        #     self.updateJsonAnalyses(analysis_name, jsonanalyses, {"selected": False})
        #     return True

        # log.info("Do something here Tomas :) ")

        try:
            a, d, dx = agmisc.AnalyzeAPK(jsonanalyses['filename'])

            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"analyzed": True})

            log.debug("Analysis completed")
            # log.info("Time spent: " + str(round(t_end - t_start, 1)) + " s")

            target_sdk = a.get_target_sdk_version()
            log.debug("Target API: " + str(target_sdk))

            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"target_api": target_sdk})

            min_sdk = a.get_min_sdk_version()
            log.debug("Minimum API: " + str(min_sdk))

            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"min_api": min_sdk})

            classes = list(dx.get_classes())

            log.debug("Number of classes found: " + str(len(classes)))

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

            classes_name = list(dict.fromkeys(classes_name))
            methods_name = list(dict.fromkeys(methods_name))
            api_methods_name = list(dict.fromkeys(api_methods_name))

            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"classes": classes_name})
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"methods": methods_name})
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"api_methods": api_methods_name})

            # Intents
            # The dictonary value is the name of each is the name of the respective activity, service or receiver

            # Parsing the AndroidManifest.xml
            root = a.get_android_manifest_xml()
            regex = re.compile('.*name$')

            if root is None:
                log.warning("This APK doesn't contain any manifest")
            else:
                for child1 in root:
                    if child1.tag == 'application':
                        for app_comp in child1:  # app_compt.tag -> activity or service or receiver
                            for child3 in app_comp:  # child3.tag -> intent-filter
                                if child3.tag == 'intent-filter':

                                    # Parse the name of the component
                                    name_attrib = list(filter(regex.match, app_comp.attrib.keys()))[0]

                                    # if 'name' in app_comp.attrib.keys():
                                    if name_attrib:
                                        if app_comp.attrib[name_attrib].startswith('.'):
                                            comp_name = root.attrib['package'] + app_comp.attrib[name_attrib]
                                        else:
                                            comp_name = app_comp.attrib[name_attrib]
                                    else:
                                        comp_name = "no_name"

                                    # Create a new entry with the name of the components
                                    intent_filters[app_comp.tag][comp_name] = {}
                                    this_comp = intent_filters[app_comp.tag][comp_name]

                                    for child4 in child3:  # child4.tag -> action or category or data
                                        if child4.tag == 'action' or child4.tag == 'category':
                                            # Create the list if it doesn't exists
                                            if child4.tag not in this_comp.keys():
                                                this_comp[child4.tag] = []
                                            c4iter = child4.attrib.iterkeys()
                                            for attrib in c4iter:
                                                this_comp[child4.tag].append(child4.attrib[attrib])
                                                log.debugv(app_comp.tag + " " + comp_name + " " + child4.tag + " " + child4.attrib[attrib])

            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"intent_filters": intent_filters})

        except Exception as e:
            excp_name = str(type(e).__name__)
            excp_module = str(e.__module__)
            my_e = str(excp_module + "." + excp_name + ": " + str(e))
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"analyzed": False})
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"error": my_e})
            log.warning("Couldn't decode with Androguard: " + my_e)
            return True
        # From activities

        # for activity in a.get_activities():
        #     intents = a.get_intent_filters('activity', activity)
        #     if len(intents):
        #         intent_filters['activities'][activity] = intents

        # # From services

        # for service in a.get_services():
        #     intents = a.get_intent_filters('service', service)
        #     if len(intents):
        #         intent_filters['services'][service] = intents

        # # From receivers

        # for receiver in a.get_receivers():
        #     intents = a.get_intent_filters('receiver', receiver)
        #     if len(intents):
        #         intent_filters['receivers'][receiver] = intents

        # self.updateJsonAnalyses(analysis_name, jsonanalyses, {"intent_filters": intent_filters})

        # a.get_intent_filters('activity',act0)

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
