from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native

class XPNative(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    NB_WORKERS = 2
    SIMULATE_JSON_WRITE = False

    def __init__(self):
        self.analyses = []

        self.analyses.append((Apktool(self), None))
        self.analyses.append((Native(self), [{"Apktool":{"status":"done"}}]))
#        self.analyses.append((InstallTest(self), [{"Native":{"native_methods": True}}]))