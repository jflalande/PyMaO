import os
import json
import logging
import threading


log = logging.getLogger("orchestrator")


"""
Get a job and launch the missing analyses.

This class is executed in a separate thread.
"""
def doJob(queue, xp):
    xp.tid = str(threading.get_ident())
    log.debug("Working on thread " + xp.tid)


    while True:
        jsondata = queue.get()
        log.debug("Worker: " + str(jsondata))

        # End of jobs
        if jsondata == "--END--":
            break;

        apkname = next(iter(jsondata))
        jsonanalyses = jsondata[apkname]

        # Looking at each analysis to see if the status is done
        # if not, do the analysis
        for analysis in xp.analyses:
            # print("==========+> " + str(analysis.__dict__))
            analysis_name = analysis.__class__.__name__

            # Setup of the working directory
            xp.setupWorkingDirectory()

            if analysis_name in jsonanalyses:
                if jsonanalyses[analysis_name]["status"] != "done":
                    doAnalysis(analysis, analysis, apkname, jsonanalyses)
            else:
                doAnalysis(analysis, analysis_name, apkname, jsonanalyses)

            # Clean of the working directory
            xp.cleanWorkingDirectory()

        # Erasing .json file
        writeJson(apkname, xp, jsondata)

"""
Perform an analysis
"""
def doAnalysis(analysis, analysis_name, apkname, jsonanalyses):
    log.info("Worker: ==== Performing analysis " + analysis_name + " on " + apkname + ".apk ====")

    # Running analysis
    analysis.run(analysis, analysis_name, apkname, jsonanalyses)

    # Finally, writes the JSON file
    jsonanalyses[analysis_name] = {"status" : "done" }


"""Rewrites the JSON file for an apk"""
def writeJson(name, xp, jsondata):
    jsonfilename = os.path.join(xp.JSONBASE, name + ".json")

    if not xp.SIMULATE_JSON_WRITE:
        with open(jsonfilename, 'w') as json_file:
            json.dump(jsondata, json_file)
    else:
        log.debug("Worker: JSON SIMULATION Writing in " + str(jsonfilename) + ': ' + str(jsondata))