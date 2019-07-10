import configparser
import ast

class Config:
    debug = "normal"
    nb_workers = 1
    devices = []
    tmpfs = None
    sdkhome = None
    targetXP = None
    apkbase = None
    jsonbase = None
    targetsymlink = None
    simulate_json_write = False
    triggerdroid_path = None

    def __init__(self, args):
        config_filename = args["config"]
        verbose = args["v"]
        simulate = args["simulate_json_write"]

        confparser = configparser.ConfigParser()
        config_file = open(config_filename, "r")
        confparser.read_file(config_file)

        self.debug = confparser['general']['debug']
        if verbose is not None:
            if verbose == 1:
                self.debug = "verbose"
            else:
                self.debug = "veryverbose"

        self.nb_workers = int(confparser['general']['nb_workers'])
        self.devices = ast.literal_eval(confparser['general']['devices'])
        self.tmpfs = confparser['general']['tmpfs']
        self.sdkhome = confparser['general']['sdkhome']


        self.targetXP = confparser['xp']['targetXP']
        self.apkbase = confparser['xp']['apkbase']
        self.jsonbase = confparser['xp']['jsonbase']
        self.targetsymlink = confparser['xp']['targetsymlink']
        self.simulate_json_write = simulate or confparser['xp']['simulate_json_write'].lower == "true"

        self.triggerdroid_path = confparser['analyses']['triggerDroidPath']

        config_file.close()
