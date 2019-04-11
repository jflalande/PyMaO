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

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Check for native methods in the smali code
        self.analyses.append((Native(self), [{"Apktool":{"status":"done"}}]))

        # Decode the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self, checkRunnableAndroidVersion=24), [{"Native":{"native_methods":True}}]))

#        self.analyses.append((InstallTest(self), [{"Native":{"native_methods": True}}]))



# manifest decoding
# check version API:  max >= 22 >= min
# copy APK


# Autre XP dyn
# install tel
# lance + sleep 1s + check PS
# uninstall