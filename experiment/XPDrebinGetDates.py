from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding

import os

class XPExampleModel(Experiment):

    def appendAnalysis(self):

        self.analyses.append((ManifestDecoding(self),None))

        # Run Unzip
        self.analyses.append((Unzip(self), None))

        # Run GetManifAndDexDates
        self.analyses.append((GetManifAndDexDates(self),
                            [{"Unzip":{"status": "done"}}]))
