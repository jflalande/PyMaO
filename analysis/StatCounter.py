from analysis.Analysis import Analysis
import logging
import os
from collections import defaultdict

log = logging.getLogger("orchestrator")

class StatCounter(Analysis):

    def dependencies(self):
        return ["Apktool"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running StatCounter analysis.")

        output_json = defaultdict(lambda: set())
        output_json['methods'] = set()
        output_json['packages'] = set()

        command = "grep -Ehr \"\\.class L.*;\" ./apktool/"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)
        with open(self.xp.working_directory+"/log") as f:
            for line in f:
                # Line is ".class Lcom/package/classname;"

                try:
                    line = line.split(' ')[1]
                    line = line[1:line.rfind('/')]

                    line = line.replace('/', '.')

                    output_json['packages'].add(line)
                except ValueError:
                    pass

        command = "grep -Er \"\\.method (private|static|public|protected|constructor) \" ./apktool/"
        errcode, res = self.xp.exec_in_subprocess(command, cwd=True, logOutputs=True)
        with open(self.xp.working_directory+"/log") as f:
            for line in f:
                # Line is "./apktool/smali/com/kensvalley/SimpleTodoList/bg.smali:.method protected onCreate(Landroid/os/Bundle;)V"
                try:
                    line = line[:line.find('.smali')] + '/' + line[line.rfind(' ')+1:line.rfind('(')]

                    line = line[line.find('/')+1:]
                    line = line[line.find('/')+1:]
                    line = line[line.find('/')+1:]

                    line = line.replace('/', '.')

                    output_json['methods'].add(line)
                except ValueError:
                    pass

        output_json = {k: list(v) for k, v in output_json.items()}
        self.updateJsonAnalyses(analysis_name, jsonanalyses, output_json)

        # This analysis cannot fail
        return True
