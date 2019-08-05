import logging
import configparser
import ast
import os.path

log = logging.getLogger("orchestrator")

class Config:
    debug = "normal"
    nb_workers = 1
    devices = []
    tmpfs = None
    sdkhome = None
    log_trace = False
    no_analysis_clean = False

    targetXP = None
    apkbase = None
    jsonbase = None
    targetsymlink = None
    simulate_json_write = False

    triggerdroid_path = None
    heuristicsfile = None

    conf_structure = {'general' : ['nb_workers', 'devices', 'tmpfs', 'sdkhome', 'debug', 'no_analysis_clean', 'log_trace'],
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
        self.no_analysis_clean = confparser.getboolean('general','no_analysis_clean')
        self.log_trace = confparser.getboolean('general','log_trace')


        self.targetXP = confparser['xp']['targetXP']
        try:
            self.apkbase = ast.literal_eval(confparser['xp']['apkbase'])
            self.jsonbase = ast.literal_eval(confparser['xp']['jsonbase'])
            self.targetsymlink = ast.literal_eval(confparser['xp']['targetsymlink'])
        except SyntaxError:
            # Backward compatibility with old dataset config style
            # i.e. one dataset without quotes
            self.apkbase = ast.literal_eval(confparser['xp']['apkbase'])
            self.jsonbase = ast.literal_eval(confparser['xp']['jsonbase'])
            self.targetsymlink = ast.literal_eval(confparser['xp']['targetsymlink'])
        self.simulate_json_write = simulate or confparser.getboolean('xp','simulate_json_write')
        
        self.triggerdroid_path = confparser['analysis']['triggerdroid_path']
        self.heuristics_file = confparser['analysis']['heuristics_file']

        config_file.close()

        self.check_config_parameters()


    def check_config_parameters(self):
        if type(self.apkbase) != type(self.jsonbase) or type(self.apkbase) != type(self.targetsymlink):
            
            log.error ("Error in configuration file: apkbase, jsonbase and targetsymlink must all have the same type (list or string).")
            quit()
        if isinstance(self.apkbase, list):
            if len(self.apkbase) != len(self.jsonbase) or len(self.apkbase) != len(self.targetsymlink):
                
                log.error ("Error in configuration file: apk, jsonbase and targetsymlink must all have the same length (when they are lists of strings).")
                quit()

    def getJsonbase(self, apk_fullpath):
        if not isinstance(self.jsonbase, list):
            return self.jsonbase
        else:
            dirname = os.path.dirname(apk_fullpath)
            return [jsonbase for apkbase, jsonbase in
                    zip(self.apkbase, self.jsonbase) if
                    dirname.startswith(apkbase)][0]

    def getTargetsymlink(self, apk_fullpath):
        if not isinstance(self.targetsymlink, list):
            return self.targetsymlink
        else:
            dirname = os.path.dirname(apk_fullpath)

            return [targetsymlink for apkbase, targetsymlink in
                    zip(self.apkbase, self.targetsymlink) if
                    dirname.startswith(apkbase)][0]
