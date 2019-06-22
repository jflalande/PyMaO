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
def grep_date_unzip(unzip_res,search):
    for line in unzip_res.split("\n"):
        if search in line:
            date = line.strip().split(" ")
            return  date[2] + " " + date[3]
    return ""

def epoch2date(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

def date2epoch(my_time):
    return int(time.mktime(time.strptime(my_time,"%Y-%m-%d %H:%M")))

class GetManifAndDexDates(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GetManifAndDexDates analysis.")

        # unzip_path = self.xp.tmpfs + "/" + self.xp.tid  + "/" + apkname

        os.stat_float_times(False)
        # manif_date = os.path.getmtime(unzip_path + "/AndroidManifest.xml")

        command = "unzip -l \"" + jsonanalyses["filename"] + ".apk\" 2> /dev/null " #| grep -E 'AndroidManifest.xml' | head -n 1 | awk '{print $2\" \"$3}' | tr -d '\n\r'"

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        if errcode != 0:
            if not res:
                log.error("unzip command failed for " + jsonanalyses["filename"])
                return 0
            else:
                log.warning("unzip returned " + str(errcode))
        else:
            log.debug("unzip manifest succesful: got \'" + str(res) + "\'")

        date = grep_date_unzip(res,"AndroidManifest.xml")
        
        if date:
            manif_date = date2epoch(date)
            log.debug("The manifest modification time is " + epoch2date(manif_date) )
        else:
            log.debug("The APK file doesn't contain a AndroidManifest.xml file")
            manif_date = ""

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"manif_date": manif_date})

        command = "unzip -l \"" + jsonanalyses["filename"] + ".apk\" 2> /dev/null " # | grep -E 'classes.dex' | head -n 1 | awk '{print $2\" \"$3}' | tr -d '\n\r'"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        if errcode != 0:
            if not res:
                log.error("unzip command failed for " + jsonanalyses["filename"])
                return 0
            else:
                log.warning("unzip returned " + str(errcode))
        else:
            log.debug("unzip dex succesful: got '" + str(res) + "'")

        date = grep_date_unzip(res,"classes.dex")

        if date:
            dex_date = date2epoch(date)
            log.debug("The classes.dex modification time is " + epoch2date(dex_date) )
        else:
            log.debug("The APK file doesn't contain any classes.dex file")
            dex_date = ""

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_date": dex_date})

        return 1
