from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class Apktool(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running Apktool analysis.")
        command = "apktool decode -r " + self.xp.APKBASE + "/" + apkname + ".apk"
        log.debug(command)

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)


