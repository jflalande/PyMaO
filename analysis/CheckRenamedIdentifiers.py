from analysis.Analysis import Analysis
import logging
import os
import re
import zipfile

from androguard.core.bytecodes.dvm import DalvikVMFormat

log = logging.getLogger("orchestrator")

class CheckRenamedIdentifiers(Analysis):

    def dependencies(self):
        return ["Apktool"]

    # Case: variable_name
    REXEPR_GET_ALPHA = re.compile('[^a-zA-Z]+')
    def _split_id_by_underscore(self, s):
        return self.REXEPR_GET_ALPHA.split(s)
        # return s.split('_')

    # Case: variableName or VariableName
    REXEPR_GET_WORDS = re.compile('[A-Z][^A-Z]*|[^A-Z]+')
    def _split_id_by_maj(self, s):
        return self.REXEPR_GET_WORDS.findall(s)

    # ws has to be sorted, uniq, alpha only and lower case, len > 3
    def _are_words(self, ws):
        corrects = []
        w = ws[0]
        ws = ws[1:]
        with open(os.path.join(os.path.dirname(__file__), '..', 'res', 'wlist.txt'), encoding="latin-1") as f:
            for l in f:
                if w < l[:-1]:
                    if len(ws) == 0:
                        return corrects
                    else:
                        w = ws[0]
                        ws = ws[1:]
                if w == l[:-1]:
                    corrects.append(w)
                    if len(ws) == 0:
                        return corrects
                    else:
                        w = ws[0]
                        ws = ws[1:]
        return corrects

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Running CheckRenamedIdentifiers analysis.")

        # Get all DEX files
        apk = zipfile.ZipFile(jsonanalyses["filename"])
        dexs = [dex_file for dex_file in apk.infolist()
               if dex_file.filename.startswith("classes")
               and dex_file.filename.endswith(".dex")]

        id_set = set()

        # Todo: If one word of an identifier is recognized, then the identifier is not renamed
        
        # For each DEX file get the classes, methods and fields identifiers
        for dex in dexs:
            d = DalvikVMFormat(apk.read(dex))

            for c in d.get_classes():
                c.get_name()
                cls_id = c.name[c.name.rfind('/')+1:c.name.find(';')]
                for w in self._split_id_by_maj(cls_id):
                    id_set.update(self._split_id_by_underscore(cls_id))
                # id_set.update(self._split_id_by_maj(cls_id))
                # id_set.update(self._split_id_by_underscore(cls_id))

            for m in d.get_methods():
                mtd_id = m.get_name()
                for w in self._split_id_by_maj(mtd_id):
                    id_set.update(self._split_id_by_underscore(mtd_id))
                # id_set.update(self._split_id_by_maj(mtd_id))
                # id_set.update(self._split_id_by_underscore(mtd_id))

            for f in d.get_fields():
                fld_id = f.get_name()
                for w in self._split_id_by_maj(fld_id):
                    id_set.update(self._split_id_by_underscore(fld_id))
                # id_set.update(self._split_id_by_maj(fld_id))
                # id_set.update(self._split_id_by_underscore(fld_id))

        correct_word = self._are_words(sorted([w.lower() for w in list(id_set) if w.isalpha() and len(w)>3]))

        self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                {"nb_word_identifier": len(correct_word),
                                 "nb_non_word_identifier": len(id_set) - len(correct_word),
                                 "non_word_identifier_ratio": (len(id_set)-len(correct_word)) / len(id_set)})

        # This analysis cannot fail
        return True
