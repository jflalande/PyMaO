from analysis.Analysis import Analysis
import logging
import os

log = logging.getLogger("orchestrator")

"""
Built one dot file containing a CFG for each method in the apk
This analysis reliies on ForceCFI  
"""


class BuildMethodsCFG(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Building CFG per methods ..")

        ### WARNING ###
        # Have to become some parameters, not hardcoded
        jar_path = "/Users/vviettri/Documents/malware/malware-trigger-dev/ForceCFI/forcecfi.jar"
        output_dir = "/Users/vviettri/Documents/malware/malware-xp/output-xp-cfg_res"
        graph_dir = "/Users/vviettri/Documents/malware/malware-xp/output-xp-cfgDot"+ "/" + apkname
        #graph_dir = "./output-xp-cfgDot"
        heuristics_file = "/Users/vviettri/Documents/malware/malware-trigger-dev/SuspiciousHeuristics/heuristics/suspicious2.json"
        ### WARNING ###


        apk =self.xp.APKBASE + "/" + apkname + ".apk"

        current_dir = os.path.abspath(os.curdir)

        os.chdir(os.path.dirname(os.path.abspath(jar_path)))
        command_java = " ".join([
            "java", "-jar", jar_path,
            "-inputApk", apk,
            "-outputDir", output_dir,
            "-dotOutputDir", graph_dir,
            "-heuristics", heuristics_file ,
            "-verbose"])

        command_chdir = "cd "+str(os.path.dirname(os.path.abspath(jar_path)))

        command=command_chdir+" ;  "+command_java


        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        list_dot = [entry for entry in os.scandir(graph_dir) if (not entry.name.startswith('.') and entry.is_file())]

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"nbMethods": len(list_dot)})

        os.chdir(current_dir)


        # This analysis can fail or not I don't know at this time
        return errcode == 0

