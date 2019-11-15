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

        # Decodes the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self),[]))

        # Runs AdbInstall
        self.analyses.append((AdbInstall(self),  [{"ManifestDecoding": {"status": "done"}}]))

        # Launches the application and test if it survives
        self.analyses.append((LaunchAndSurvive(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"ManifestDecoding": {"launchable": True}},
                               {"AdbInstall" : {"install": True }}]))

        # Runs AdbUninstall if installed
        self.analyses.append((AdbUninstall(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"AdbInstall" : {"install": True }}]))



