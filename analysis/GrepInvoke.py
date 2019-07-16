from analysis.Analysis import Analysis
import logging
import os
from collections import defaultdict

log = logging.getLogger("orchestrator")

class GrepInvoke(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running GrepInvoke analysis.")

        command = "grep -Ehr \"invoke-(direct|virtual|super)\" ./apktool/"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)

        output_json = defaultdict(lambda: defaultdict(lambda: 0))

        with open(self.xp.working_directory+"/log") as f:
            for line in f:
                # Line is "invoke {arg0,...,argn}, classname->method(params)ret"

                # Get only the method descriptor
                line = line.split(',')[-1]

                # Remove args and ret type
                line = line.split('(')[0]

                # Remove ';' and first 'L' and replace '/' to .''
                line = line[2:].replace(';','').replace('/','.')

                cls, meth = line.split('->')

                output_json[cls][meth] += 1

        self.updateJsonAnalyses(analysis_name, jsonanalyses, output_json)

        # This analysis cannot fail
        return True
