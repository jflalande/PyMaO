from analysis.Analysis import Analysis
import logging
import os

log = logging.getLogger("orchestrator")

class GrepReflection(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GrepReflection analysis.")

        command = "grep -Ehr \"invoke-(direct|virtual|super) .*, Ljava/lang/reflect/Method;->invoke\" ./apktool/"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)

        reflection_usage = False
        if os.path.getsize(self.xp.working_directory+"/log") > 0:
            reflection_usage = True

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"reflection_usage": reflection_usage})

        # This analysis cannot fail
        return True
