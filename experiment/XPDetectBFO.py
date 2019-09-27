from experiment.Experiment import Experiment

from analysis.DetectBFO import DetectBFO
from analysis.SymlinkAPK import SymlinkAPK

class XPDetectBFO(Experiment):

    def appendAnalysis(self):
        self.analyses.append((DetectBFO(self),[]))

        self.analyses.append((SymlinkAPK(self),
                              [{"DetectBFO": {"found_empty_bytecode": True}}]))
