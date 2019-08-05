from analysis.Analysis import Analysis
import logging
import re
import time
from collections import defaultdict

log = logging.getLogger("orchestrator")



class DHTCheck(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
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
        classes_per_libs = defaultdict(lambda:defaultdict(int))
        REGEX = "^.*\[DHT\]([^ ]*)( [^/][^ ]*|)( /[^ ]*|)$"
        regex = re.compile(REGEX)
        for line in res.split("\n"):
            m = regex.match(line)
            if m: # this line contains DHT
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHT": True})
                
                # Counting
                #print("GROUPS:" + str(m.groups()))
                classname = m.group(1)
                fieldname = m.group(2)
                libname = m.group(3)
                if libname:
                    libnames[libname] += 1
                if classname:
                    classnames[classname] += 1

                if libname and classname:
                    #print("libname: " + libname)
                    #print("classname: " + classname)
                    #print("update: =================> " + str(dict(classes_per_libs)))
                    classes_per_libs[libname][classname] += 1

        if classnames:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTclassnames": dict(classnames)})
        if libnames:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTlibnames": dict(libnames)})
        if classes_per_libs:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTclassesperlibs": dict(classes_per_libs)})

        # Dumping in a file for DEBUG purpose
        filename = jsonanalyses["filename"]
        log.debug("Dumping in the file: " + self.xp.getJsonbase(filename) + basename + ".log")
        with open(self.xp.getJsonbase(filename) + "/" + basename + ".log" , "w" ) as f:
            f.write(res)

        return True


