from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")


class GetDEXSize(Analysis):

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GetDEXSize analysis")

        command = "unzip -l \"" + jsonanalyses["filename"] + "\" | grep ' classes.dex' | awk '{ print $1 }'"

        errcode, res = self.xp.exec_in_subprocess(command, cwd=True)

        if errcode != 0:
            if not res:
                log.error("unzip command failed for " + jsonanalyses["filename"])
                self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_size": None})
                return 1
            else:
                log.warning("unzip returned " + str(errcode))
        else:
            log.debug("unzip successful: got \'" + str(res) + "\'")

        dex_size = int(res)

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {"dex_size": dex_size})

        return 1

