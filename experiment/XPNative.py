from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native

class XPNative(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    NB_WORKERS = 2
    SIMULATE_JSON_WRITE = True

    def __init__(self):
        self.analyses = []

        self.analyses.append(Apktool(self))
        self.analyses.append(Native(self))
