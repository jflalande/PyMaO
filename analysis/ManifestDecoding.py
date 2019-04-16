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

        # try:
        #     for level in ["minSdkVersion", "targetSdkVersion", ""]:
        #         matched_lines = [line for line in res.split('\n') if level in line]
        #         log.debugv("Matched line: " + str(matched_lines))
        #         if len(matched_lines) == 1:
        #             # Converting:
        #             #       A: android:minSdkVersion(0x0101020c)=(type 0x10)0x18
        #             # into  24
        #             SdkVersion = int(matched_lines[0].split('=')[1].split(')')[1],16)
        #             self.updateJsonAnalyses(analysis_name, jsonanalyses, {level: SdkVersion})
        # except ValueError: # For exampe, some manifest contains 0x13 (Raw: "19"
        #     log.warning("Error decoding the Manifest for the matched lines:")
        #     log.warning(str(matched_lines))
        #     return False
        for line in res.split('\n'  ):

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



        # We want to check if a specific Android version is reached
        if self.checkRunnableAndroidVersion != -1:

            # Some ugly malware has no minSdkVerion !
            if "minSdkVersion" not in jsonanalyses[analysis_name]:
                return False  # Analysis fails

            self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                    {"checkRunnableAndroidVersion" : jsonanalyses[analysis_name]["minSdkVersion"]
                                    <= self.checkRunnableAndroidVersion })

        # This analysis can fail if aapt fails to analyze apk
        return errcode == 0


