from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")



class AdbUninstall(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running analysis Uninstall using Adb.")

        package_name = jsonanalyses["ManifestDecoding"]["package"]

        exitcode, res = self.xp.adb_send_command(["uninstall", package_name ])

        for line in res.split('\n'):
            if "Success" in line:
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"uninstall": True})
                return True

        return False


