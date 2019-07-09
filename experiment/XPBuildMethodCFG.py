from experiment.Experiment import Experiment

from analysis.BuildMethodsCFG import BuildMethodsCFG
from analysis.ManifestDecoding import ManifestDecoding

class XPBuildMethodCFG(Experiment):

    def appendAnalysis(self):

        self.analyses.append((BuildMethodsCFG(self),[]))

