from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native
from analysis.ManifestDecoding import ManifestDecoding
from analysis.SymlinkAPK import SymlinkAPK

class XPNative(Experiment):

    APKBASE = "/media/jf/B006AF9A06AF5FD8/androzoo/samples"
    JSONBASE = "/media/jf/B006AF9A06AF5FD8/orchestrator/XPNative/jsons"
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
        self.analyses.append((SymlinkAPK(self, targetDirectory="/media/jf/B006AF9A06AF5FD8/orchestrator/XPNative/apk"),
                              [{"ManifestDecoding" : {"checkRunnableAndroidVersion": True}}]))



# install tel
# lance + sleep 1s + check PS
# uninstall