from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")



class AdbInstall(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running analysis Install using Adb. Grant all permissions.")

        exitcode, res = self.xp.adb_send_command(["install", "-g", "-r", self.xp.APKBASE + "/" + apkname + ".apk" ])

        for line in res.split('\n'):
            if "Success" in line:
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"install": True})
                return True
            if "FAILED" in line:
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"install": False})
                return True

        return False


