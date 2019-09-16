from experiment.Experiment import Experiment

from analysis.Apkid import Apkid
from analysis.Apktool import Apktool
from analysis.CheckEncryptedStrings import CheckEncryptedStrings
from analysis.CheckRenamedIdentifiers import CheckRenamedIdentifiers
from analysis.Native import Native
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.GrepDCL import GrepDCL
from analysis.GrepReflection import GrepReflection
from analysis.Packer import Packer

class XPObfuStats(Experiment):

    def appendAnalysis(self):
        # Get APK data
        self.analyses.append((GetManifAndDexDates(self), None))

        # Run Apkid
        self.analyses.append((Apkid(self), None))

        # Check for packer detection in Apkid output
        self.analyses.append((Packer(self),
                              [{"Apkid": {"status": "done"}}]))

        # Run Apktool
        self.analyses.append((Apktool(self),
                              [{"Packer" : {"packer": False}}]))

        # Check for native methods in the smali code
        self.analyses.append((Native(self),
                              [{"Packer" : {"packer": False}}]))

        # Check for dynamic class loading usage in the smali code
        self.analyses.append((GrepDCL(self),
                              [{"Packer" : {"packer": False}}]))

        # Check for reflection usage in the smali code
        self.analyses.append((GrepReflection(self),
                              [{"Packer" : {"packer": False}}]))

        # Check if strings are encrypted
        self.analyses.append((CheckEncryptedStrings(self),
                              [{"Packer" : {"packer": False}}]))

        # Check if identifiers are renamed
        self.analyses.append((CheckRenamedIdentifiers(self),
                              [{"Packer" : {"packer": False}}]))
