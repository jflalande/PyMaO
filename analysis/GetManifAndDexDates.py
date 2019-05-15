from analysis.Analysis import Analysis
import logging
import os
import time
import datetime

log = logging.getLogger("orchestrator")

"""
GetManifAndDexDates may fail
Errors are captured.
"""

def epoch_to_date(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

class GetManifAndDexDates(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running GetManifAndDexDates analysis.")

        unzip_path = self.xp.TMPFS + "/" + self.xp.tid  + "/" + apkname

        os.stat_float_times(False)
        manif_date = os.path.getmtime(unzip_path + "/AndroidManifest.xml")
        log.debug("The manifest modification time is " + epoch_to_date(manif_date) )

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"manif_date": manif_date})

        dex_date = os.path.getmtime(unzip_path + "/classes.dex")
        log.debug("The manifest modification time is " + epoch_to_date(dex_date) )

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_date": dex_date})

        return 1
