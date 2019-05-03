from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding

import os

class XPExampleModel(Experiment):

    HOME = os.path.expanduser('~') # Names can changes

    APKBASE = HOME + "/gits/malware-goodware-small-dataset"
    JSONBASE = HOME + "/orch/malware_json"
    TARGETSYMLINK =  HOME + "/orch/nativeAPK"

    SIMULATE_JSON_WRITE = False

    def __init__(self, deviceserial=None):
        self.analyses = []

        self.analyses.append((ManifestDecoding(self),None))

        # Run Unzip
        self.analyses.append((Unzip(self), None))

        # Run GetManifAndDexDates
        self.analyses.append((GetManifAndDexDates(self),
                            [{"Unzip":{"status": "done"}}]))
