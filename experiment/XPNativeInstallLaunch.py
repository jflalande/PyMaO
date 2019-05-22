from experiment.Experiment import Experiment

from analysis.Apktool import Apktool
from analysis.Native import Native
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbInstall import AdbInstall
from analysis.AdbUninstall import AdbUninstall
from analysis.LaunchAndSurvive import LaunchAndSurvive
from analysis.SymlinkAPK import SymlinkAPK

class XPNativeInstallLaunch(Experiment):

    #APKBASE = "/media/jf/B006AF9A06AF5FD8/androzoo/samples"
    #JSONBASE = "/media/jf/B006AF9A06AF5FD8/orchestrator/XPNative/jsons"
    #TARGETSYMLINK = "/media/jf/B006AF9A06AF5FD8/orchestrator/XPNative/apk"

    APKBASE = "/home/jf/swap/malwaredebug"
    JSONBASE = "/home/jf/swap/malwaredebug"
    TARGETSYMLINK = "/home/jf/swap/nativeAPK"


    ''' By defautl, an XP does not use a drvice '''
    def usesADevice(self):
        return True

    def __init__(self, deviceserial=None):
        self.analyses = []

        # Run Apktool
        self.analyses.append((Apktool(self), None))

        # Check for native methods in the smali code
        self.analyses.append((Native(self), None))

        # Decode the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self, checkRunnableAndroidVersion=24),
                              [{"Native":{"lib64_or_suspicious": True}}]))

        # Run AdbInstall
        self.analyses.append((AdbInstall(self),  [{"ManifestDecoding": {"checkRunnableAndroidVersion": True}}]))

        # Launch the application and test if it survives
        self.analyses.append((LaunchAndSurvive(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"ManifestDecoding": {"launchable": True}},
                               {"AdbInstall" : {"install": True }}]))

        # Run AdbUninstall if installed
        self.analyses.append((AdbUninstall(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"AdbInstall" : {"install": True }}]))

        # Copying the APK that are Native and with API > 24 to a specific folder
        self.analyses.append((SymlinkAPK(self, targetDirectory=self.TARGETSYMLINK),
                              [{"LaunchAndSurvive" : {"running": True}}]))


