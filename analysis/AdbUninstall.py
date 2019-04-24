from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")



class AdbUninstall(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running analysis Uninstall using Adb.")

        package_name = jsonanalyses["ManifestDecoding"]["package"]

        exitcode, res = self.xp.adb_send_command(["uninstall", package_name ])

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"uninstall": exitcode == 0})

        return True


