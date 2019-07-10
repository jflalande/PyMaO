from analysis.Analysis import Analysis
import logging
import os
import pygraphviz as pgv

log = logging.getLogger("orchestrator")

def num_lines_in_file(fname):
    with open(fname, "r") as f:
        res = []
        for line in f:
            if line not in res:
                res.append(line)
        return len(res)

def find(L,x):
    for i in range(len(L)):
        if x in L[i]:
            return i
    return None

def union(L, x, y):
    ix = find(L, x)
    iy = find(L, y)
    if ix != iy:
        L[ix] = L[ix] + L[iy]
        del L[iy]

def connected_components(G):
    components = [[n] for n in G.nodes()]
    for (f,t) in G.edges():
        union(components, f, t)
    return components


class FindGraftingPoint(Analysis):

    def dependencies(self):
        return []


    def analysis(self, analysis, analysis_name, basename, jsonanalyses):
        log.debug("Finding grafting point ..")

        apk = jsonanalyses["filename"]

        current_dir = os.path.abspath(os.curdir)

        cfg = pgv.AGraph(self.xp.working_directory + "/call-graph.dot")

        #cfg.edges, cfg.nodes
        edges = cfg.edges()
        nodes = cfg.nodes()

        susp_file = open(self.xp.working_directory + "/extraction.json")
        lines = []
        for l in susp_file:
            l = l.strip()
            lines.append(l)
        susp_file.close()

        susp = [n for n in nodes if n.attr['label'] in lines]
        susp_edges = [(f,t) for (f,t) in edges if f in susp and t in susp]

        for n in nodes:
            if n not in susp:
                cfg.remove_node(n)

        conn = connected_components(cfg)
        self.updateJsonAnalyses(analysis_name, jsonanalyses,
                                {
                                    'nbConnectedComponents': len(conn),
                                    'connectedComponentsSize': list(map(len,conn))
                                })

        cfg.draw("/tmp/"+os.path.basename(apk)+".png", prog='dot')


        errcode = 0

        os.chdir(current_dir)

        # This analysis can fail or not I don't know at this time
        return errcode == 0

