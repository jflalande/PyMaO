from analysis.Analysis import Analysis
import logging
import time
from collections import defaultdict

log = logging.getLogger("orchestrator")



class DHTCheck(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running analysis Launch and test if app survives.")

        # Wake up and unlock device
        self.xp.wake_up_and_unlock_device()


        package_activity_name = jsonanalyses["ManifestDecoding"]["package"] + "/"
        for activity in jsonanalyses["ManifestDecoding"]["activities"]:
            if "main" in activity and activity["main"]:
                log.debug("Using activity: " + str(activity))
                if '.' not in activity["name"]: # The name of the package is not given: adding a dot
                    package_activity_name = package_activity_name + "."
                package_activity_name = package_activity_name + activity["name"].replace("$","\$")
                break; # Launching first found main activity

        log.debug("Computed package/activity name to launch: " + package_activity_name)

        # dumpsys package com.ex.pg.bypassjnileak |grep userId | cut -d "=" -f 2 > /data/local/tmp/traced_uid
        exitcode, res = self.xp.adb_send_command(
            ("shell dumpsys package " + jsonanalyses["ManifestDecoding"]["package"] + " |grep userId | cut -d '=' -f 2").split())
        if res == "": # Very bad error !
            return False

        exitcode, res = self.xp.adb_send_command((
            "shell echo " + res + " > /data/local/tmp/traced_uid"
                                                 ).split())
        log.debug("Setting logcat buffer size to 16MB.")
        exitcode, res = self.xp.adb_send_command(["logcat", "-G", "16M"])

        log.debug("Cleaning logcat.")
        exitcode, res = self.xp.adb_send_command(["logcat", "--clear"])

        # am start -n yourpackagename/activityname
        exitcode, res = self.xp.adb_send_command(["shell", "am", "start", "-n", package_activity_name ])

        log.debug("DHTCheck: Sleeping...")
        time.sleep(10)

        # Searching a DHT log in the logcat
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHT": False})
        exitcode, res = self.xp.adb_send_command(["logcat", "-d"])


        classnames = defaultdict(int)
        libnames = defaultdict(int)
        for line in res.split("\n"):
            if "[DHT]" in line:
                classname = line.split("[DHT]")[1].split()[0] # field is dropped
                classnames[classname] += 1
                splitted_line = line.split()
                if len(splitted_line) == 2:
                    if splitted_line[3][0] == '/':
                        libnames[splitted_line[3]] += 1
                elif len(splitted_line) == 3:
                    libnames[splitted_line[3]] += 1
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHT": True})
        if classnames:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTclassnames": dict(classnames)})
        if libnames:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTlibnames": dict(libnames)})

        # Dumping in a file for DEBUG purpose
        log.debug("Dumping in the file: " + self.xp.JSONBASE + apkname)
        with  open(self.xp.JSONBASE + "/" + apkname + ".log" , "w" ) as f:
            f.write(res)

        return True


