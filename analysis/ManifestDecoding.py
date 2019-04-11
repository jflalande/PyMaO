from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class ManifestDecoding(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running ManifestDecoding analysis.")

        command = "aapt d xmltree " + self.xp.APKBASE + "/" + apkname + ".apk AndroidManifest.xml"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        for level in ["minSdkVersion", "targetSdkVersion"]:
            matched_lines = [line for line in res.split('\n') if level in line]
            log.debugv("Matched line: " + str(matched_lines))
            if len(matched_lines) == 1:
                # Converting:
                #       A: android:minSdkVersion(0x0101020c)=(type 0x10)0x18
                # into  24
                SdkVersion = int(matched_lines[0].split('=')[1].split(')')[1],16)
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {level: SdkVersion})



        # This analysis can fail if aapt fails to analyze apk
        return errcode == 0


