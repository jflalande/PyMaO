from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.DeadMethodCounter import DeadMethodCounter
from analysis.GrepInvoke import GrepInvoke
from analysis.StatCounter import StatCounter

class XPFastStatsInvoke(Experiment):

    def appendAnalysis(self):

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Grep invoke in the smali code
        self.analyses.append((GrepInvoke(self), None))

        # Count the number of packages and methods
        self.analyses.append((StatCounter(self), None))

        # Count the number of method not invoked
        self.analyses.append((DeadMethodCounter(self), None))
