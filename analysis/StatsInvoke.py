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

    if not os.path.isfile (fname):
        log.debug("The file {} doesn't exist".format(fname))
        return -1

    with open(fname, "r") as f:
        res = []
        for line in f:
            if line not in res:
                res.append(line)
    return len(res)

class StatsInvoke(Analysis):

    def dependencies(self):
        return []

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Building CFG per methods ..")

        ### WARNING ###
        # Have to become some parameters, not hardcoded
        jar_path = self.xp.config.triggerdroid_path

        output_dir = self.xp.working_directory
        temp_dir = ""
        heuristics_file = self.xp.config.heuristics_file
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

        res={}
        if os.path.isfile (output_dir + "/allInvoke.json") :

            with open(output_dir + "/allInvoke.json", "r") as invokeFile:
                for line in invokeFile:
                    package=line.split(",")[0]
                    method =line.split(",")[1]
                    method=method.replace('\n','')

                    if package in res :
                        if method in res[package] :
                            res[package][method]+=1
                        else :
                            res[package][method] = 1
                    else :
                        res[package]={}
                        res[package][method] = 1
        else :
            log.debug("The file allInvoke.json  doesn't exist")


        for package in res :
            totalCall =0
            for method in res[package]:
                totalCall = totalCall + res[package][method]
            res[package]["TOTALCALL"]=totalCall


        self.updateJsonAnalyses(analysis_name, jsonanalyses, res)

        os.chdir(current_dir)

        
        # This analysis can fail or not I don't know at this time
        return errcode == 0

