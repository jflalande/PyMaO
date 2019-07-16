from experiment.Experiment import Experiment

from analysis.Apkid import Apkid
from analysis.Packer import Packer
from analysis.SymlinkAPK import SymlinkAPK

class XPPacker(Experiment):

    def appendAnalysis(self):

        # Run Apkid
        self.analyses.append((Apkid(self), None))

        # Check for packer detection in Apkid output
        self.analyses.append((Packer(self),
                              [{"Apkid": {"status": "done"}}]))

        # Copying the APK that are detected using a packer
        self.analyses.append((SymlinkAPK(self),
                              [{"Packer" : {"packer": True}}]))
