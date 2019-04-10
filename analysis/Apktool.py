from analysis.Analysis import Analysis

from command_subprocessor import exec_in_subprocess

class Apktool(Analysis):



    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        print("Running Apktool analysis.")
        command = "apktool decode -r " + self.xp.APKBASE + "/" + apkname + ".apk"
        print(command)

        errcode, res = exec_in_subprocess(command)
        print(res)

