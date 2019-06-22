from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbInstall import AdbInstall
from analysis.SymlinkAPK import SymlinkAPK

import os

class XPExampleModel(Experiment):

    def __init__(self, deviceserial=None):
        self.deviceserial = deviceserial
        self.analyses = []

        # Analysis ManifestDecoding
        # - always gives self as a parameter to an Analysis
        # - None are the preconditions
        self.analyses.append((ManifestDecoding(self),None))

        # Run Unzip
        # - No preconditions
        self.analyses.append((Unzip(self), None))

        # Run GetManifAndDexDates
        # - Here the precondition is encoded as an array, containing a dictionary with:
        #   - as key, one of the previous analysis (here Unzip)
        #   - as value, the expected value
        self.analyses.append((GetManifAndDexDates(self),
                            [{"Unzip":{"status": "done"}}]))

        # Run AdbInstall
        # Another example:
        # this analysis install the application if
        #  - the ManifestDecoding succeeds
        #  - the unzip succeeds
        # Additionnaly, the analysis will use a device.
        # self.analyses.append((AdbInstall(self),  [{"Unzip":{"status": "done"}}, {"ManifestDecoding": {"status": "done"}}]))

        # Make a symbolic link to APK that have some criteria
        # in this example, it makes a symbolic link if the install is a success
        # myout-apk/XXX.apk --------> myinpt-apk/XXX.apk
        #self.analyses.append((SymlinkAPK(self),
        #                  [{"AdbInstall" : {"install": True }}]))