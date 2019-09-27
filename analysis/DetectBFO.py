from analysis.Analysis import Analysis
from collections import defaultdict
import logging

import scipy.stats
import lief

log = logging.getLogger("orchestrator")

class DetectBFO(Analysis):

    def dependencies(self):
        return []

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running DetectBFO analysis.")

        oat = lief.parse(jsonanalyses["filename"])

        # Check that we are analyzing an OAT file
        if type(oat) is not lief._pylief.OAT.Binary:
            return False

        # Map bytecode and quick code
        mapping_bytecode_quick = defaultdict(lambda:{'quick': "", 'bytecode': ""})
        for cls in oat.classes:
            for meth in cls.methods:
                if lief.DEX.ACCESS_FLAGS.NATIVE not in meth.dex_method.access_flags:
                    mapping_bytecode_quick[cls.fullname+meth.name]['quick'] = meth.quick_code
                    mapping_bytecode_quick[cls.fullname+meth.name]['bytecode'] = meth.dex_method.bytecode

        # Compute ratio len(quick) / len(bytecode)
        # And check for empty bytecode with populated quick
        divs = []
        suspicious_empty_bytecode = False
        for methname, codes in mapping_bytecode_quick.items():
            bytecode = codes['bytecode']
            quick = codes['quick']
            if len(quick) > 0:
                if len(bytecode) > 0:
                    divs.append((len(quick), len(bytecode)))
                else:
                    suspicious_empty_bytecode = True

        # Compute diff entropies
        entropies = []
        for methname, codes in mapping_bytecode_quick.items():
            if len(codes['quick']) > 0:
                if len(codes['bytecode']) > 0:
                    entropies.append((scipy.stats.entropy(codes['bytecode']), scipy.stats.entropy(codes['quick'])))

        self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                {"found_empty_bytecode": suspicious_empty_bytecode,
                                 "list_ratio": divs,
                                 "list_entropise": entropies})

        return True
