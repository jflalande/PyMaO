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

def epoch2date(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def date2epoch(my_time):
    return int(time.mktime(time.strptime(my_time,"%Y-%m-%d %H:%M")))

class GetManifAndDexDates(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running GetManifAndDexDates analysis.")

        # unzip_path = self.xp.TMPFS + "/" + self.xp.tid  + "/" + apkname

        os.stat_float_times(False)
        # manif_date = os.path.getmtime(unzip_path + "/AndroidManifest.xml")

        command = "unzip -l \"" + self.xp.APKBASE + "/" + apkname + ".apk\" | grep -E 'AndroidManifest.xml' | awk '{print $2\" \"$3}'"

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        if errcode != 0:
            log.error("unzip command failed for " + apkname)
            return 0
        else:
            res = res.replace("\n","")
            log.debug("unzip succesful: got \'" + str(res) + "\'")

        manif_date = date2epoch(res)

        log.debug("The manifest modification time is " + epoch2date(manif_date) )

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"manif_date": manif_date})

        command = "unzip -l \"" + self.xp.APKBASE + "/" + apkname + ".apk\" | grep -E 'classes.dex' | awk '{print $2\" \"$3}'"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        if errcode != 0:
            log.error("unzip command failed for " + apkname)
            return 0
        else:
            res = res.replace("\n","")
            log.debug("unzip succesful: got '" + str(res) + "'")

        dex_date = date2epoch(res)

        log.debug("The manifest modification time is " + str(epoch2date(dex_date)) )

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_date": dex_date})

        return 1
