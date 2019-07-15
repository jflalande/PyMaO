from analysis.Analysis import Analysis
import logging
import json
import os

log = logging.getLogger("orchestrator")

class Packer(Analysis):

    def dependencies(self):
        return ["Apkid"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running Packer analysis.")

        apkid_json_filename = os.path.join(self.xp.working_directory, 'apkid', os.path.basename(jsonanalyses["filename"]))
        apkid_json = json.load(open(apkid_json_filename))

        m = apkid_json['files'][0]['matches']
        if 'packer' in m:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"packer" : True})
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"packer_name" : m['packer']})
        else:
            self.updateJsonAnalyses(analysis_name, jsonanalyses, {"packer" : False})

        # This nalaysis cannot fail
        return True
