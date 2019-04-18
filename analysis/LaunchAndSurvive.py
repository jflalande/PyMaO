from analysis.Analysis import Analysis
import logging
import time

log = logging.getLogger("orchestrator")



class LaunchAndSurvive(Analysis):

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

        # am start -n yourpackagename/activityname
        exitcode, res = self.xp.adb_send_command(["shell", "am", "start", "-n", package_activity_name ])

        log.debug("LaunchAndSurvive: Sleeping...")
        time.sleep(2)

        log.debug("Touching screen")
        # Closing app requires to touch the screen in case of error
        # adb shell input tap 1000 1000
        exitcode, res = self.xp.adb_send_command(["shell", "input", "tap", "1000", "1000"])

        log.debug("LaunchAndSurvive: Sleeping...")
        time.sleep(1)

        exitcode, res = self.xp.adb_send_command(["shell", "pidof", jsonanalyses["ManifestDecoding"]["package"]])
        log.debug("Detected PID of " + jsonanalyses["ManifestDecoding"]["package"] + " : " + res)
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"running": res != ""})

        return True


