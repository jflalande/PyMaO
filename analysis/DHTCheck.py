from analysis.Analysis import Analysis
import logging
import time

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

        log.debug("Setting logcat buffer size to 16MB.")
        exitcode, res = self.xp.adb_send_command(["logcat", "-G", "16M"])

        log.debug("Cleaning logcat.")
        exitcode, res = self.xp.adb_send_command(["logcat", "--clear"])

        # am start -n yourpackagename/activityname
        exitcode, res = self.xp.adb_send_command(["shell", "am", "start", "-n", package_activity_name ])

        log.debug("DHTCheck: Sleeping...")
        time.sleep(3)

        log.debug("Touching screen")
        # Closing app requires to touch the screen in case of error
        # adb shell input tap 1000 1000
        exitcode, res = self.xp.adb_send_command(["shell", "input", "tap", "1000", "1000"])

        # Searching a DHT log in the logcat
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHT": False})
        exitcode, res = self.xp.adb_send_command(["logcat", "-d", "-e", "DHT"])
        for line in res.split("\n"):
            if "[DHT]" in line:
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHT": True})
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"DHTLine": line})
                break

        return True


