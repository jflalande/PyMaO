from analysis.Analysis import Analysis
import logging
import os

log = logging.getLogger("orchestrator")

# https://developer.android.com/reference/java/lang/ClassLoader
cls_loaders = [
    "java.lang.ClassLoader",
    "dalvik.system.BaseDexClassLoader",
    "java.security.SecureClassLoader",
    "dalvik.system.DelegateLastClassLoader",
    "dalvik.system.DexClassLoader",
    "dalvik.system.InMemoryDexClassLoader",
    "dalvik.system.PathClassLoader",
    "java.net.URLClassLoader"
]

class GrepDCL(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GrepDCL analysis.")

        command = "grep -Ehr \"(%s)\" ./apktool/" % "|".join(cls_loaders)
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)

        dcl_usage = False
        if os.path.getsize(self.xp.working_directory+"/log") > 0:
            dcl_usage = True

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dcl_usage": dcl_usage})

        # This analysis cannot fail
        return True
