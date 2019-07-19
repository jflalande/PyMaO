from analysis.Analysis import Analysis
import logging

log = logging.getLogger("orchestrator")

class DeadMethodCounter(Analysis):

    def dependencies(self):
        return ["GrepInvoke", "StatCounter"]

    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        # TODO: we could split methods by package

        methods = jsonanalyses['StatCounter']['methods']
        invoked = jsonanalyses['GrepInvoke']
        dead_pck = set()
        dead_methods = set()
        for m in methods:
            pck = m[:m.rfind('.')]
            if pck in invoked:
                cms = invoked[pck]
                if not m in cms:
                    dead_methods.add(m)
            else:
                dead_methods.add(m)
                dead_pck.add(pck)

        self.updateJsonAnalyses(analysis_name, jsonanalyses, {'dead_pck': list(dead_pck), 'dead_methods': list(dead_methods)})

        # This analysis cannot fail
        return True
