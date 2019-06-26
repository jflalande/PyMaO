import os
import json
import logging
import threading
from utils.Statistics import Statistics

log = logging.getLogger("orchestrator")


"""
Get a job and launch the missing analyses.

This class is executed in a separate thread.
"""
def doJob(queue, xp, worker_nb):
    xp.tid = str(threading.get_ident())
    xp.worker_nb = worker_nb
    log.debug("Working on thread " + xp.tid)

    setupHasBeenDone = False

    while True:

        # Preparing the device the first time and arming watchdog
        if not setupHasBeenDone:
            xp.setupDeviceUsingAdb()
            setupHasBeenDone = True

        # Getting a job to perform
        jsondata = queue.get()

        # End of jobs
        if jsondata == "--END--":
            if xp.usesADevice():
                xp.cleanDeviceUsingAdb()
            break;

        # This is a real job - we decrease the number of jobs instatistics
        Statistics.decNbJobs()

        apkname = next(iter(jsondata))
        jsonanalyses = jsondata[apkname]

        log.info("Worker " + str(xp.worker_nb) + " : Job " + str(Statistics.getNbJobs()) + " ==== Doing " + str(apkname) + ".apk ====")

        # Setup of the working directory
        xp.setupWorkingDirectory()
        log.debug("Working directory is "+os.path.abspath(os.curdir))

        status = {}
        for analysis, precondition in xp.analyses[::-1]:
            analysis_name = analysis.__class__.__name__
            status[analysis_name] = "No"

        for analysis, precondition in xp.analyses[::-1]:
            analysis_name = analysis.__class__.__name__
            if analysis_name not in jsonanalyses:
                status[analysis_name] = "Todo"
            if status[analysis_name] == "Todo":
                for analysis_dependency_name in analysis.dependencies():
                    status[analysis_dependency_name] = "Todo"
                    if analysis_dependency_name not in status:
                        raise Exception("The analysis " + analysis_dependency_name + " is missing as a dependency of " + analysis_name + ".")


        # Looking at each analysis to see if the status is done, the preconditions and dependencies
        # Determines if each analysis should be done
        for analysis, precondition in xp.analyses:
            analysis_name = analysis.__class__.__name__
            log.debugv("Considering analysis named: " + analysis_name + " with precondition " + str(precondition))

            if status[analysis_name] == "Todo":
                # Checking the status and preconditions of this analysis before executing it
                analysisPrecondition = evaluatePreConditions(analysis_name, jsonanalyses, precondition)
                log.debug("Precondition result: " + str(analysisPrecondition))
                if not analysisPrecondition:
                    analysis.updateJsonAnalyses(analysis_name, jsonanalyses, {"status": "precond_false"})
                else:
                    # We setup the JSON entry for this analysis with a first write:
                    analysis.updateJsonAnalyses(analysis_name, jsonanalyses, {"status": "doing"})

                    # Checking device status
                    if xp.usesADevice():
                        xp.check_device_online_or_wait_reboot()

                    # We launch the analysis
                    log.debug("Worker " + str(xp.worker_nb) + " : Job " + str(
                        Statistics.getNbJobs()) + " ==== Performing analysis " + str(analysis_name) + " on " + str(
                        apkname) + ".apk ====")
                    analysis.run(analysis, analysis_name, apkname, jsonanalyses)

            # Updating statistics
            Statistics.recordXPResult(analysis_name, jsonanalyses)

        # Clean of the working directory
        xp.cleanWorkingDirectory()



        # Erasing .json file
        writeJson(apkname, xp, jsondata)
        log.debug("Finished " + apkname + " -- JSON: " + str(jsondata))



"""Rewrites the JSON file for an apk"""
def writeJson(name, xp, jsondata):
    jsonfilename = os.path.join(xp.jsonbase, name + ".json")

    with open(jsonfilename, 'w') as json_file:
        json.dump(jsondata, json_file, indent=4)


def evaluatePreConditions(analysis_name, jsonanalyses, precondition):
    log.debug("Evaluating preconditions " + str(precondition) + " for analysis " + analysis_name)
    if precondition is None:
        return True

    # Checking all preconditions i.e. the state of the previous analyses
    for cond in precondition:
        log.debugv("Condition: " + str(cond))
        log.debugv("Current JSON data: " + str(jsonanalyses))
        for past_analysis, testconditions in cond.items():
            current_data_for_this_tool = jsonanalyses[past_analysis]
            for onecondition_key, onecondition_value in testconditions.items():
                if onecondition_key not in current_data_for_this_tool:
                    return False
                if current_data_for_this_tool[onecondition_key] != onecondition_value:
                    return False

    log.debugv("Conditions are ALL good :)")
    return True
