
from analysis.Analysis import Analysis
import logging
import os

log = logging.getLogger("orchestrator")


class Native(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running Native analysis.")

        command = "grep -Er \"\.method.* native \""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"native_methods" : res != ""})

        #command = "grep -r \"arm64\""
        command = "find ./apktool/lib -name \"arm64*\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"arm64": "./apktool/lib/arm64" in res})

        command = "find ./apktool/lib -name \"armeabi\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"armeabi": "./apktool/lib/armeabi" in res})

        command = "stat ./apktool/lib"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"libdirexists": errcode == 0})

        lib64_or_suspicious = jsonanalyses["Native"]["arm64"] or \
            (not jsonanalyses["Native"]["libdirexists"] and jsonanalyses["Native"]["native_methods"])
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"lib64_or_suspicious": lib64_or_suspicious})

        # This analysis cannot fail
        return True
