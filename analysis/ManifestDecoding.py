from analysis.Analysis import Analysis
import logging
import re

log = logging.getLogger("orchestrator")


class ManifestDecoding(Analysis):

    regexAttributes = {
        # android:minSdkVersion(0x0101020c)=(type 0x10)0x3
        "minSdkVersion" : "^\s+A: android:minSdkVersion\(\w+\)=\([\w ]+\)(\w+)[\w ]*$",
        "targetSdkVersion" : "^\s+A: android:targetSdkVersion\(\w+\)=\([\w ]+\)(\w+)[\w ]*$",
        "package" : "^\s+A: package=\"([\w\.]+)\".*$"
    }

    # Sending a specific parameter: the version of Android we want to check against this APK
    def __init__(self, xp_, checkRunnableAndroidVersion=-1):
        super().__init__(xp_)
        self.checkRunnableAndroidVersion = checkRunnableAndroidVersion

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running ManifestDecoding analysis.")

        command = "aapt d xmltree '" + self.xp.APKBASE + "/" + apkname + ".apk' AndroidManifest.xml"

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)



        # Single value capture: minSdkVersion, targetSdkVersion, package
        for line in res.split('\n'):

            for attribute in self.regexAttributes:
                regex = self.regexAttributes[attribute]
                m = re.match(regex, line)

                if m:
                    val = m.group(1)
                    try:
                        if attribute == "minSdkVersion" or attribute == "targetSdkVersion":
                            val = int(val, 16) # Tranforming 0x18 in int value
                        self.updateJsonAnalyses(analysis_name, jsonanalyses, {attribute: val})
                    except ValueError:  # For exampe, some manifest contains 0x13 (Raw: "19"
                        log.warning("Error decoding the Manifest for the matched lines:")
                        log.warning(str(line))

        # Activity decoding + detection of main activity
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"launchable": False})
        activity = None
        activities = []
        # Number of activities
        NofActivities = 0
        indent = 1000
        for line in res.split('\n'):
            # Detecting a new activity tag or other tag indented on the current activity
            m = re.match("^(\s+)E:.*$", line)
            if m:
                current_indent = len(m.group(1))
                if current_indent <= indent:
                    if activity is not None:
                        log.debugv("ManifestDecoding: pushing activity: " + str(activity))
                        activities.append(activity)
                        indent = 1000
                        activity = None

            # Detecting a start of activity
            m = re.match("^(\s+)E: activity.*$", line)
            if m:
                log.debugv("ManifestDecoding: start of activity detected.")
                activity = {}
                indent = len(m.group(1))


            # Detecting the name of the activity
            # The name can contain caracters, dots, and $
            m = re.match("^(\s+)A: android:name\(\w+\)=\"([\w\.\$]+)\".*$", line)
            if m and len(m.group(1)) == indent + 2:
                log.debugv("ManifestDecoding: name of activity detected.")
                activity["name"] = m.group(2)
                NofActivities += 1

            # Detecting the MAIN activity
            m = re.match("^(\s+)A: android:name\(\w+\)=\"(android\.intent\.action\.MAIN)\".*$", line)
            # If the indent increases and the name of activity has been captured by the regex
            if m and len(m.group(1)) > indent and "name" in activity:
                log.debugv("ManifestDecoding: LAUNCHER intent of activity detected.")
                activity["main"] = True
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"launchable": True})

        # Updating JSON: Number of activities NumActivities
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"NumActivities": NofActivities})

        # Pushing last activity
        if activity is not None:
            activities.append(activity)

        # Updating JSON
        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"activities": activities})

        # We want to check if a specific Android version is reached
        if self.checkRunnableAndroidVersion != -1:

            # Some ugly malware has no minSdkVersion !
            if "minSdkVersion" not in jsonanalyses[analysis_name]:
                return False  # Analysis fails

            self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                    {"checkRunnableAndroidVersion" : jsonanalyses[analysis_name]["minSdkVersion"]
                                    <= self.checkRunnableAndroidVersion })

        # This analysis can fail if aapt fails to analyze apk
        return errcode == 0
