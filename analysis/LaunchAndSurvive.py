from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")



class LaunchAndSurvive(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        log.debug("Running analysis Launch and test if app survives.")

        exitcode, res = self.xp.adb_send_command(["shell", "pm", "list" ])



        return True


