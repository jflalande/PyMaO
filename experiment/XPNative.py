from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native
from analysis.ManifestDecoding import ManifestDecoding
from analysis.CopyAPK import CopyAPK

class XPNative(Experiment):

    APKBASE = "/media/jf/B006AF9A06AF5FD8/androzoo/samples"
    JSONBASE = "/home/jf/orchestrator/jsons"
    SIMULATE_JSON_WRITE = False

    def __init__(self):
        self.analyses = []

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Check for native methods in the smali code
        self.analyses.append((Native(self), None))

        # Decode the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self, checkRunnableAndroidVersion=24),
                              [{"Native":{"native_methods":True}}]))

        # Copying the APK that are Native and with API > 24 to a specific folder
        self.analyses.append((CopyAPK(self, targetDirectory="/home/jf/orchestrator/nativeOutput"),
                              [{"ManifestDecoding" : {"checkRunnableAndroidVersion": True}}]))



# install tel
# lance + sleep 1s + check PS
# uninstall