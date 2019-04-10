from experiment.Experiment import Experiment

import analysis.Apktool as Apktool
import analysis.Native as Native



class XPNative(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    NB_WORKERS = 2
    SIMULATE_JSON_WRITE = True

    def __init__(self):
        self.analyses = []

        self.analyses.append(Apktool)
        self.analyses.append(Native)
