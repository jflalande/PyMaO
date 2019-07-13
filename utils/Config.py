import logging
import configparser
import ast

log = logging.getLogger("orchestrator")

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
    noanalysisclean = False
    triggerdroid_path = None
    heuristicsfile = None

    conf_structure = {'general' : ['nb_workers', 'devices', 'tmpfs', 'sdkhome', 'debug', 'noanalysisclean'],
                      'xp': ['targetxp', 'apkbase', 'jsonbase', 'simulate_json_write', 'targetsymlink'],
                      'analysis': ['triggerdroid_path', 'heuristics_file']}

    def check_config_file(self,cp):
        for s in cp.sections():
            if s not in self.conf_structure.keys():
                log.error("Unknown section {} in config file\n".format(s))
            for v in cp[s].keys():
                if v not in self.conf_structure[s]:
                    log.error("Unexpected parameter {} in section {}\n".format(v,s))

    def __init__(self, args):
        config_filename = args["config"]
        verbose = args["v"]
        simulate = args["simulate_json_write"]

        confparser = configparser.ConfigParser()
        config_file = open(config_filename, "r")
        confparser.read_file(config_file)

        self.check_config_file(confparser)

        self.debug = confparser['general']['debug']
        if verbose is not None:
            if verbose == 1:
                self.debug = "verbose"
            else:
                self.debug = "veryverbose"

        self.nb_workers = confparser.getint('general','nb_workers')
        self.devices = ast.literal_eval(confparser['general']['devices'])
        self.tmpfs = confparser['general']['tmpfs']
        self.sdkhome = confparser['general']['sdkhome']


        self.targetXP = confparser['xp']['targetXP']
        self.apkbase = confparser['xp']['apkbase']
        self.jsonbase = confparser['xp']['jsonbase']
        self.targetsymlink = confparser['xp']['targetsymlink']
        self.simulate_json_write = simulate or confparser.getboolean('xp','simulate_json_write')

        self.triggerdroid_path = confparser['analysis']['triggerdroid_path']
        self.heuristics_file = confparser['analysis']['heuristics_file']

        config_file.close()
