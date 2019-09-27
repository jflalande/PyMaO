from analysis.Analysis import Analysis
import logging
import numpy as np
import scipy.stats
import zipfile
from collections import defaultdict

from androguard.core.bytecodes.dvm import DalvikVMFormat

log = logging.getLogger("orchestrator")

class CheckFilteredEncryptedStrings(Analysis):

    def dependencies(self):
        return []

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running CheckEncryptedStrings analysis.")

        try:
            # Get all DEX files
            try:
                apk = zipfile.ZipFile(jsonanalyses["filename"])
            except zipfile.BadZipFile:
                return False
            dexs = [dex_file for dex_file in apk.infolist()
                   if dex_file.filename.startswith("classes")
                   and dex_file.filename.endswith(".dex")]

            # List all identifiers to remove them from string pool before computing the entropy
            id_set = set()
            for dex in dexs:
                d = DalvikVMFormat(apk.read(dex))

                for c in d.get_classes():
                    c.get_name()
                    cls_id = c.name[c.name.rfind('/')+1:c.name.find(';')]
                    id_set.add(cls_id)

                for m in d.get_methods():
                    id_set.add(m.get_name())

                for f in d.get_fields():
                    id_set.add(f.get_name())

            mapping_len_entropy = defaultdict(lambda:[])
            alphabet = set()
            current_avg = 0
            nb_entropy = 0
            nb_over_1 = 0
            nb_over_2 = 0
            nb_over_3 = 0
            nb_over_4 = 0
            nb_over_5 = 0
            nb_over_6 = 0
            nb_over_7 = 0
            # strings = ""
            # For each DEX file get all the strings
            for dex in dexs:
                d = DalvikVMFormat(apk.read(dex))
                for s_info in d.strings:
                    # s = s_info.get_unicode()
                    s = s_info.get_data().decode('latin1')

                    # If the string is not an identifier
                    if s not in id_set:

                        # Compute the entropy
                        _, counts = np.unique([c for c in s], return_counts=True)
                        e = scipy.stats.entropy(counts)

                        alphabet.update(list(s))
                        mapping_len_entropy[len(s)].append(e)

                        # Update the average entropy
                        # https://math.stackexchange.com/questions/106700/incremental-averageing
                        nb_entropy += 1
                        current_avg = current_avg + ((e - current_avg) / nb_entropy)

                        if e > 1:
                            nb_over_1 += 1
                        if e > 2:
                            nb_over_2 += 1
                        if e > 3:
                            nb_over_3 += 1
                        if e > 4:
                            nb_over_4 += 1
                        if e > 5:
                            nb_over_5 += 1
                        if e > 6:
                            nb_over_6 += 1
                        if e > 7:
                            # strings += str(s)
                            nb_over_7 += 1

            # current_deviation = 0
            # nb_entropy = 0
            # # For each DEX file get all the strings
            # for dex in dexs:
            #     d = DalvikVMFormat(apk.read(dex))
            #     for s_info in d.strings:
            #         s = s_info.get_unicode()

            #         # Compute the entropy
            #         _, counts = np.unique([c for c in s], return_counts=True)
            #         e = scipy.stats.entropy(counts)

            #         # Update the average entropy
            #         # https://math.stackexchange.com/questions/106700/incremental-averageing
            #         nb_entropy += 1
            #         current_deviation = current_deviation + ((pow(e-current_avg, 2) - current_deviation) / nb_entropy)

            self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                    {"average_string_entropy": current_avg,
                                     "nb_string": nb_entropy,
                                     "nb_over_1": nb_over_1,
                                     "nb_over_2": nb_over_2,
                                     "nb_over_3": nb_over_3,
                                     "nb_over_4": nb_over_4,
                                     "nb_over_5": nb_over_5,
                                     "nb_over_6": nb_over_6,
                                     "nb_over_7": nb_over_7,
                                     # "strs": strings,
                                     "entropies_by_len": dict(mapping_len_entropy),
                                     "alphabet": str(alphabet),
                                     "alphabet_size": len(alphabet)})
                                     # "std_deviation_entropy": current_deviation})

            return True
        except:
            return False
