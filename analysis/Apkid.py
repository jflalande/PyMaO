from analysis.Analysis import Analysis
import os
import logging

log = logging.getLogger("orchestrator")

class Apkid(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running APKiD analysis.")

        # Decodes all resources in an apktool sub folder of the worker
        command = "apkid -j " + jsonanalyses["filename"]
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)

        # This analysis can fail if apktool fails to analyze apk
        apkid_json_filename = os.path.join(self.xp.working_directory, 'log')

        return errcode == 0 and os.path.isfile(apkid_json_filename)
