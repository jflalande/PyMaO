from experiment.Experiment import Experiment
# from analysis.SymlinkAPK import SymlinkAPK
from analysis.SelectAPK import SelectAPK
from analysis.GetAPKSize import GetAPKSize
from analysis.Androguard import Androguard
from analysis.GetManifAndDexDates import GetManifAndDexDates


class XPSelectAPK(Experiment):

    def appendAnalysis(self):

        # Run GetAPKSize
        self.analyses.append((GetAPKSize(self), None))

        # Run GetManifAndDexDates
        self.analyses.append((GetManifAndDexDates(self), [{"GetAPKSize": {"status": "done"}}]))

        # Run Androguard (API level)
        self.analyses.append((Androguard(self), [{"GetManifAndDexDates": {"status": "done"}}]))

        # Run SelectAPK
        # self.analyses.append((SelectAPK(self), [{"Androguard": {"status": "done"}}]))

        # Copying the APK that were selected
        # self.analyses.append((SymlinkAPK(self),[{"SelectAPK": {"selected": True}}]))



