
from analysis.Analysis import Analysis


class Native(Analysis):

    def analysis(self, analysis, analysis_name, apkname, jsonanalyses):
        print("Running Native analysis.")