from experiment.Experiment import Experiment
from analysis.SymlinkAPK import SymlinkAPK
from analysis.SelectAPK import SelectAPK


class XPSelectAPK(Experiment):

    def appendAnalysis(self):

        # Run SelectAPK
        self.analyses.append((SelectAPK(self), None))

        # Copying the APK that were selected
        # self.analyses.append((SymlinkAPK(self),
                              # [{"SelectAPK": {"selected": True}}]))



