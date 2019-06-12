from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding
from analysis.GetAPKSize import GetAPKSize

import os

class XPUnzipAndAnalyse(Experiment):

    HOME = os.path.expanduser('~') # Names can changes

    # APKBASE = HOME + "/gits/malware-goodware-small-dataset"
    # JSONBASE = HOME + "/orch/malware_json"

    APKBASE = HOME + "/malware_datasets/amd/liens"
    # APKBASE = HOME + "/malware_datasets/drebin/malware/sample"
    JSONBASE = HOME + "/orch/amd"

    TARGETSYMLINK =  HOME + "/orch/nativeAPK"

    SIMULATE_JSON_WRITE = False

    def __init__(self, deviceserial=None):
        self.analyses = []

        # Run GetAPKSize
        self.analyses.append((GetAPKSize(self),None))

        # Run GetManifAndDexDates
        self.analyses.append((GetManifAndDexDates(self), None))

        # Run ManifestDecoding
        self.analyses.append((ManifestDecoding(self), None))

        # Run Unzip
        # self.analyses.append((Unzip(self), None))
