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

        command = "aapt d xmltree " + self.xp.APKBASE + "/" + apkname + ".apk AndroidManifest.xml"

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

        # Activity decoding
        activity = None
        activities = []
        indent = 1000
        for line in res.split('\n'):
            print(line)
            # Detecting a new activity tag or other tag indented on the current activity
            m = re.match("^(\s+)E:.*$", line)
            if m:
                current_indent = len(m.group(1))
                if current_indent <= indent:
                    if activity is not None:
                        activities.append(activity)
                        indent = 1000
                        activity = None

            # Detecting a start of activity
            m = re.match("^(\s+)E: activity.*$", line)
            if m:
                activity = {}
                indent = len(m.group(1))

            # Detecting the name of the activity
            m = re.match("^(\s+)A: android:name\(\w+\)=\"([\w\.]+)\".*$", line)
            if m and len(m.group(1)) == indent + 2:
                activity["name"] = m.group(2)

            # Detecting the MAIN activity
            m = re.match("^(\s+)A: android:name\(\w+\)=\"(android\.intent\.action\.MAIN)\".*$", line)
            if m and len(m.group(1)) > indent:
                activity["main"] = True

        # Pushing last activity
        if activity is not None:
            activities.append(activity)

        # Updateing JSON
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


