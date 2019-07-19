from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native
from analysis.ManifestDecoding import ManifestDecoding
from analysis.SymlinkAPK import SymlinkAPK

class XPNativeWithoutArch(Experiment):

    def appendAnalysis(self):

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Check for native methods in the smali code
        self.analyses.append((Native(self), None))

        # Copying the APK that are Native and with API > 24 to a specific folder
        self.analyses.append((SymlinkAPK(self),
                              [{"Native" : {"native_methods": True}}]))


