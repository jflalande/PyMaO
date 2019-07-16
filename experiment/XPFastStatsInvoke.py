from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.GrepInvoke import GrepInvoke

class XPFastStatsInvoke(Experiment):

    def appendAnalysis(self):

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Grep invoke in the smali code
        self.analyses.append((GrepInvoke(self), None))
