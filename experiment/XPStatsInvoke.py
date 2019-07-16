from experiment.Experiment import Experiment

from analysis.StatsInvoke import StatsInvoke


class XPStatsInvoke(Experiment):

    def appendAnalysis(self):

        self.analyses.append((StatsInvoke(self),[]))
        #self.analyses.append((FindGraftingPoint(self),[
        #    {'BuildMethodsCFG': {'status': 'done'}}]))

