import os
import json
import logging
from utils.Statistics import Statistics
from json import JSONDecodeError

log = logging.getLogger("orchestrator")

def getRecursiveFilenames(basedir):
    log.debugv("Walking folder " + str(basedir))
    for (dirpath, _, filenames) in os.walk(basedir):
        for filename in filenames:
            log.debugv("This is filename " + filename)
            yield os.path.join(dirpath,filename)

def createJobs(queue, xp):

    # Cleaning TMPFS
    xp.cleanTMPFSDirectory()

    log.info("Producer: iterating over apk files in " + str(xp.config.apkbase) + " - It can take some time...")
    for filename in getRecursiveFilenames(xp.config.apkbase):
        if filename.endswith(".apk"):
            log.debugv("Producer: doing " + filename)
            basename = getMalwareName(filename)
            log.debugv("Producer: basename " + basename)

            # Reading the JSON backup for this malware from the disk
            json = readJson(basename, xp)
            json[basename]["filename"] = filename # Storing filename
            # At this stage, the JSON file is:
            # { hashcode: { "filename" : "/var/here/hashcode.apk" }}
            log.debugv("Producer: json " + str(json))

            # Determine if one of the analysis should be done for this apk
            analysisToDo = redoAnalyses(basename, json, xp)
            log.debugv("Redo analysis: " + str(analysisToDo))

            # Debug
            #if Statistics.getNbJobs() > 10:
            #    return

            # If one of the analyses have to be redone, queue it
            if analysisToDo:
                queue.put(json)
                Statistics.incNbJobs()


def redoAnalyses(packagename, json, xp):
    """
    json = {
    { "sha256" : {
    "analysis.Apktool" : { "status" : "done"},
    "analysis.Native" : { "status" : "done"}
    "analysis.XXX" : { "status" : "failed"}
    "analysis.YYYY" : { }   // but dependency is Apktool
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
    log.debugv("Producer: evaluating if one of the analysis has to be performed for " + packagename)
    # Looking at each analysis to see if the status is done
    log.debugv("Current loaded JSON: " + str(jsonanalyses))
    for analysis, precondition in xp.analyses:
        #print("============ "+ str((analysis.__class__.__name__)))
        analysis_name = analysis.__class__.__name__
        log.debugv("Considering analysis " + analysis_name)
        if analysis_name in jsonanalyses:
            log.debugv("Current status for analysis " + analysis_name + " : " + str(jsonanalyses[analysis_name]))
            #if jsonanalyses[analysis_name]["status"] != "failed":
            #    return True
        else:
            return True

    return False


def getMalwareName(filename):
    return os.path.splitext(os.path.basename(filename))[0]

def readJson(name, xp):
    jsonfilename = os.path.join(xp.config.jsonbase, name + ".json")
    log.debugv("Producer: will read JSON " + str(jsonfilename))

    try:
        if not os.path.isfile(jsonfilename):
            return { name : {}}
        else:
            with open(jsonfilename) as json_file:
                return json.load(json_file)
    except JSONDecodeError:
        # File is empty or contains errors
        return {name: {}}
