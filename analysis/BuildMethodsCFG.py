from analysis.Analysis import Analysis
import logging
import os
import pygraphviz as pgv
from shutil import copyfile

log = logging.getLogger("orchestrator")

"""
Built one dot file containing a CFG for each method in the apk
This analysis reliies on ForceCFI  
"""

def num_lines_in_file(fname):
    with open(fname, "r") as f:
        res = []
        for line in f:
            if line not in res:
                res.append(line)
        return len(res)

class BuildMethodsCFG(Analysis):

    def dependencies(self):
        return []

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Building CFG per methods ..")

        ### WARNING ###
        # Have to become some parameters, not hardcoded
        jar_path = self.xp.config.triggerdroid_path

        output_dir = self.xp.working_directory
        temp_dir = ""
        heuristics_file = self.xp.config.heuristicsFile
        ### WARNING ###

        apk = jsonanalyses["filename"]

        current_dir = os.path.abspath(os.curdir)

        os.chdir(os.path.dirname(os.path.abspath(jar_path)))
        command_java = " ".join([
            "java", "-jar",
            jar_path,
            "fr.inria.triggerdroid.analysis.Main",
            "-vg", "-o", output_dir,
            "-m", "ORIGIN",
            "-w", "ALL",
            "-a", jsonanalyses['filename'],
            "-d",
            self.xp.config.sdkhome+"/platforms",
            "-e", heuristics_file])

        command_chdir = "cd "+str(os.path.dirname(os.path.abspath(jar_path)))

        command=command_chdir+" ;  "+command_java


        # TriggerDroid is launched
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)

        #copyfile(self.xp.working_directory+"heuristicAnalyzed.json", self.xp.output_dir+"/"+basename+"_"+"heuristicAnalyzed.json")



        #test si le fichier a été crée
        if os.path.isfile(output_dir+"/heuristic.json")  :
            copyfile(output_dir+"/heuristic.json","/Users/vviettri/Documents/malware/malware-xp/output-xp/"+basename+"_"+"heuristic.json")

        if os.path.isfile (output_dir + "/call-graph.dot") :
            cfg = pgv.AGraph(output_dir + "/call-graph.dot")
        else :
            log.debug("The file call-graph.dot doesn't exist")

        if os.path.isfile (output_dir +  "/global.json"):
            nb_suspicious = num_lines_in_file(output_dir + "/global.json")
        else :
            log.debug("The file global.json doesn't exist")

        if os.path.isfile (output_dir +  "/extraction.json"):
            nb_data_dependency = num_lines_in_file(output_dir + "/extraction.json")
        else :
            log.debug("The file extraction.json doesn't exist")

        if os.path.isfile (output_dir +  "/sms.json"):
            nb_sms = num_lines_in_file(output_dir + "/sms.json")
        else :
            log.debug("The file sms.json doesn't exist")

        if os.path.isfile (output_dir +  "/binary.json"):
            nb_binary = num_lines_in_file(output_dir + "/binary.json")
        else :
            log.debug("The file binary.json doesn't exist")

        if os.path.isfile (output_dir +  "/dynamic.json") :
            nb_dynamic = num_lines_in_file(output_dir + "/dynamic.json")
        else :
            log.debug("The file dynamic.json doesn't exist")

        if os.path.isfile (output_dir +  "/network.json"):
            nb_network = num_lines_in_file(output_dir + "/network.json")
        else :
            log.debug("The file network.json doesn't exist")

        if os.path.isfile (output_dir +  "/telephony.json"):
            nb_telephony = num_lines_in_file(output_dir + "/telephony.json")
        else :
            log.debug("The file telephony.json doesn't exist")

        if os.path.isfile (output_dir +"/crypto.json"):
            nb_crypto = num_lines_in_file(output_dir + "/crypto.json")
        else :
            log.debug("The file crypto.json doesn't exist")

        #TODO ajouter le traitement de l'exception
        nb_cats = sum(map(lambda x: 1 if x != 0 else 0,
                          [nb_sms, nb_binary, nb_dynamic, nb_telephony, nb_crypto, nb_network]))

        # list_dot = [entry for entry in os.scandir(output_dir) if (not entry.name.startswith('.') and entry.is_file())]

        self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                {"nbMethods": nb_methods,
                                 "nbSuspicious": nb_suspicious,
                                 "nbDataDependency": nb_data_dependency,
                                 "nbSms": nb_sms,
                                 "nbBinary": nb_binary,
                                 "nbDynamic": nb_dynamic,
                                 "nbNetwork": nb_network,
                                 "nbTelephony": nb_telephony,
                                 "nbCrypto": nb_crypto,
                                 "nbCats": nb_cats,
                                })

        os.chdir(current_dir)

        
        # This analysis can fail or not I don't know at this time
        return errcode == 0

