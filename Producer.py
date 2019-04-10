import os
import json
import logging

log = logging.getLogger("orchestrator")


def createJobs(queue, xp):

    for filename in os.listdir(xp.APKBASE):
        if filename.endswith(".apk"):
            log.debug("Producer: doing " + filename)
            packagename = getMalwareName(filename)
            log.debug("Producer: packagename " + packagename)

            json = readJson(packagename, xp)
            log.debug("Producer: json " + str(json))

            # Determine if one of the analysis should be done for this apk
            analysisToDo = redoAnalyses(packagename, json, xp)
            log.debug("Redo analysis: " + str(analysisToDo))

            # If one of the analyses have to be redone, queue it
            if analysisToDo:
                queue.put(json)




def redoAnalyses(packagename, json, xp):
    """
    json = {
    { "sha256" : {
    "analysis.Apktool" : { "status" : "done"},
    "analysis.Native" : { "status" : "done"}
    }
    }
    :param packagename: the name of the apk
    :param json: the json part that describes this apk
    :param xp: the experiment to run
    :return: True if the experiment should run for this apk
    """
    if packagename not in json:
        return True

    jsonanalyses = json[packagename]

    # Looking at each analysis to see if the status is done
    for analysis in xp.analyses:
        #print("============ "+ str((analysis.__class__.__name__)))
        analysis_name = analysis.__class__.__name__
        if analysis_name in jsonanalyses:
            if jsonanalyses[analysis_name]["status"] != "done":
                return True
        else:
            return True
    return False


def getMalwareName(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def readJson(name, xp):
    jsonfilename = os.path.join(xp.JSONBASE, name + ".json")

    if not os.path.isfile(jsonfilename):
        return { name : {}}
    else:
        with open(jsonfilename) as json_file:
            return json.load(json_file)

