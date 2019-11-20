from experiment.Experiment import Experiment

from analysis.AdbInstall import AdbInstall
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbUninstall import AdbUninstall
from analysis.LaunchAndSurvive import LaunchAndSurvive
from analysis.SymlinkAPK import SymlinkAPK
from analysis.DHTCheck import DHTCheck

# install tel
# lance + sleep 1s + check PS
# uninstall
class XPDemo(Experiment):

    SDKHOME = "/home/jf/Android/Sdk"

    ''' This XP uses a device '''
    def usesADevice(self):
        return True

    def appendAnalysis(self):

        # Decode the manifest
        self.analyses.append((ManifestDecoding(self),[]))

        # Runs AdbInstall
        self.analyses.append((AdbInstall(self),  [{"ManifestDecoding": {"status": "done"}}]))

        # Launches the application and test if it survives
        self.analyses.append((LaunchAndSurvive(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"ManifestDecoding": {"launchable": True}},
                               {"AdbInstall" : {"install": True }}]))

        # Runs adb uninstall if installed
        self.analyses.append((AdbUninstall(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"AdbInstall" : {"install": True }}]))

        # Create a symlink to the original APK in an output directory if some conditions holds:
        # - if the app has survive for the analysis LaunchAndSurvive
        # - if the targetSdkVersion equals 27
        self.analyses.append((SymlinkAPK(self),[{"LaunchAndSurvive": {"running": True}},
            {"ManifestDecoding": {"targetSdkVersion": 27}}]))


