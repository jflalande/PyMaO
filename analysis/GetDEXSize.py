from analysis.Analysis import Analysis
import logging
import time

log = logging.getLogger("orchestrator")


class GetDEXSize(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GetDEXSize analysis")

        command = "unzip -l \"" + jsonanalyses["filename"] + "\" 2> /dev/null | grep ' classes.dex' | awk '{ print $1 }'"

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        log.debug("Errorcode: " + str(errcode))
        if errcode != 0:
            # log.debug("Errorcode: " + str(errcode))
            log.error("unzip command failed for " + jsonanalyses["filename"])
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_size": None})
            return 1
        else:
            log.debug("unzip successful: got \'" + str(res) + "\'")

        try:
            dex_size = int(res)
        except ValueError:
            log.error("Something wrong happened with this APK: " + jsonanalyses['filename'])
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_size": None})
            return 1

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_size": dex_size})

        return 1

