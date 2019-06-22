from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbInstall import AdbInstall
from analysis.SymlinkAPK import SymlinkAPK
from analysis.Apktool import Apktool
from analysis.GrepSMS import GrepSMS
from analysis.BuildMethodsCFG import BuildMethodsCFG

import os

class XPCountMethods(Experiment):

    # NOT USED ANYMORE: PUT THESE IN A CONFIG FILE ! cf config/default.ini

    # Your home dir
    #HOME = os.path.expanduser('~') # Names can changes

    # The dataset folder: where all your apk are
    #APKBASE = "/Users/vviettri/Documents/malware/malware-xp/input-xp"# HOME + "/myinput"

    # The output folder where all the results will be recorded (json files)
    #JSONBASE = "/Users/vviettri/Documents/malware/malware-xp/output-xp" #HOME + "/myout-jsons"

    # Used for making a symbolic link in a new folder to the APK that are selected by your experiment
    #TARGETSYMLINK =  HOME + "/myout-apk"

    def appendAnalysis(self):

        #Run Apktool
        #self.analyses.append((Apktool(self), None))
        self.analyses.append((BuildMethodsCFG(self),None))# [{"Apktool":{"status": "done"}}]))

