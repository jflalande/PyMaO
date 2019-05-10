from experiment.Experiment import Experiment

from analysis.Unzip import Unzip
from analysis.GetManifAndDexDates import GetManifAndDexDates
from analysis.ManifestDecoding import ManifestDecoding
from analysis.AdbInstall import AdbInstall
from analysis.SymlinkAPK import SymlinkAPK
from analysis.Apktool import Apktool
from analysis.GrepSMS import GrepSMS

import os

class XPGrepSMS(Experiment):

    # Your home dir
    HOME = os.path.expanduser('~') # Names can changes

    # The dataset folder: where all your apk are
    APKBASE = "/Users/vviettri/Documents/malware/malware-trigger-dev/Demos"# HOME + "/myinput"

    # The output folder where all the results will be recorded (json files)
    JSONBASE = "/Users/vviettri/Documents/malware/malware-xp/output-xp" #HOME + "/myout-jsons"

    # Used for making a symbolic link in a new folder to the APK that are selected by your experiment
    TARGETSYMLINK =  HOME + "/myout-apk"

    SIMULATE_JSON_WRITE = False

    def __init__(self, deviceserial=None):
        self.deviceserial = deviceserial
        self.analyses = []

        #Run Apktool
        self.analyses.append((Apktool(self), None))
        self.analyses.append((GrepSMS(self), [{"Apktool":{"status": "done"}}]))

