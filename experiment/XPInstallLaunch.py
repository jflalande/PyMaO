from experiment.Experiment import Experiment

from analysis.AdbInstall import AdbInstall
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbUninstall import AdbUninstall

# install tel
# lance + sleep 1s + check PS
# uninstall
class XPInstallLauch(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    SIMULATE_JSON_WRITE = False
    SDKHOME = "/home/jf/Android/Sdk"
    devicesesrial = "CB512FEL52"

    def __init__(self):
        self.analyses = []

        # Decode the manifest and checks that the minSdkVersion is 24
        # For apps that have native methods
        self.analyses.append((ManifestDecoding(self),[]))

        # Run AdbInstall
        self.analyses.append((AdbInstall(self),  [{"ManifestDecoding": {"status": "done"}}]))

        # Run AdbUninstall if installed
        self.analyses.append((AdbUninstall(self),
                              [{"ManifestDecoding": {"status": "done"}},
                               {"AdbInstall" : {"install": True }}]))


