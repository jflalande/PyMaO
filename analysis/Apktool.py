from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")

"""
Apktool may fail, for example on code4hk, nevertheless the output code is 0 :/
Errors are sent to stderr.
"""

class Apktool(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Apktool analysis.")

        # Decodes all resources in an apktool sub folder of the worker
        command = "apktool -f -o apktool decode -r \"" + self.xp.APKBASE + "/" + apkname + ".apk\""
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        # This analysis can fail if apktool fails to analyze apk
        return errcode == 0


