from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native
from analysis.ManifestDecoding import ManifestDecoding

class XPNative(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    SIMULATE_JSON_WRITE = False

    def __init__(self):
        self.analyses = []

        self.analyses.append((Apktool(self), None))
        self.analyses.append((Native(self), [{"Apktool":{"status":"done"}}]))
        self.analyses.append((ManifestDecoding(self), [{"Native":{"status":"done"}}]))
#        self.analyses.append((InstallTest(self), [{"Native":{"native_methods": True}}]))



# manifest decoding
# check version API:  max >= 22 >= min
# copy APK


# Autre XP dyn
# install tel
# lance + sleep 1s + check PS
# uninstall