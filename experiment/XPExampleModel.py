from experiment.Experiment import Experiment

from analysis.Unzip import Unzip

class XPExampleModel(Experiment):

    APKBASE = "/home/jf/swap/malware"
    JSONBASE = "/home/jf/swap/malware"
    TARGETSYMLINK = "/home/jf/swap/nativeAPK"

    SIMULATE_JSON_WRITE = False

    def __init__(self, deviceserial=None):
        self.analyses = []

        # Run Unzip
        self.analyses.append((Unzip(self), None))

        # Run Timestamp
        #self.analyses.append((TimeStamp(self, checkFile="AndroidManifest.xml"),
        #                      [{"Unzip":{"status": "done"}}]))

