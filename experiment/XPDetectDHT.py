from experiment.Experiment import Experiment

from analysis.AdbInstall import AdbInstall
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbUninstall import AdbUninstall
from analysis.DHTCheck import DHTCheck
from analysis.SymlinkAPK import SymlinkAPK

# install tel
# lance + sleep 1s + check PS
# uninstall
class XPDetectDHT(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/DHT/jsons"
    SIMULATE_JSON_WRITE = False
    SDKHOME = "/home/jf/Android/Sdk"

    TARGETSYMLINK = "/home/jf/swap/DHT/apk"

    ''' By defautl, an XP does not use a drvice '''
    def usesADevice(self):
        return True

    def __init__(self, deviceserial=None):
        self.deviceserial = deviceserial
        self.analyses = []

        # Decode the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self),[]))

        # Run AdbInstall
        self.analyses.append((AdbInstall(self),  [{"ManifestDecoding": {"status": "done"}}]))

        # Launch the application and test if it survives
        self.analyses.append((DHTCheck(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"ManifestDecoding": {"launchable": True}},
                               {"AdbInstall" : {"install": True }}]))

        # Run AdbUninstall if installed
        self.analyses.append((AdbUninstall(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"AdbInstall" : {"install": True }}]))

        # Copying the APK that are Native and with API > 24 to a specific folder
        self.analyses.append((SymlinkAPK(self, targetDirectory=self.TARGETSYMLINK),
                              [{"DHTCheck" : {"DHT": True}}]))

