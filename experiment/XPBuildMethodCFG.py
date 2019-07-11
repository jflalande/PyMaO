from experiment.Experiment import Experiment

from analysis.BuildMethodsCFG import BuildMethodsCFG
from analysis.FindGraftingPoint import FindGraftingPoint

class XPBuildMethodCFG(Experiment):

    def appendAnalysis(self):

        self.analyses.append((BuildMethodsCFG(self),[]))
        #self.analyses.append((FindGraftingPoint(self),[
        #    {'BuildMethodsCFG': {'status': 'done'}}]))

