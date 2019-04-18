import os
import json
import logging
import threading
from experiment.Statistics import Statistics

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
        Statistics.decNbJobs()

        log.debug("Worker: " + str(jsondata))

        # End of jobs
        if jsondata == "--END--":
            break;

        apkname = next(iter(jsondata))
        jsonanalyses = jsondata[apkname]

        # Setup of the working directory
        xp.setupWorkingDirectory()

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
            # print("==========+> " + str(analysis.__dict__))
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
                    # We launch the analysis
                    doAnalysis(analysis, analysis_name, apkname, jsonanalyses)

        # Clean of the working directory
        xp.cleanWorkingDirectory()

        # Erasing .json file
        writeJson(apkname, xp, jsondata)
        log.info("Finished " + apkname + " -- JSON: " + str(jsondata))



"""
Perform an analysis
"""
def doAnalysis(analysis, analysis_name, apkname, jsonanalyses):
    log.info("Worker: Job " + str(Statistics.getNbJobs()) + " ==== Performing analysis " + str(analysis_name) + " on " + str(apkname) + ".apk ====")

    # Running analysis
    ret = analysis.run(analysis, analysis_name, apkname, jsonanalyses)

    return ret


"""Rewrites the JSON file for an apk"""
def writeJson(name, xp, jsondata):
    jsonfilename = os.path.join(xp.JSONBASE, name + ".json")

    if not xp.SIMULATE_JSON_WRITE:
        with open(jsonfilename, 'w') as json_file:
            json.dump(jsondata, json_file, indent=4)
    else:
        log.debug("Worker: JSON SIMULATION Writing in " + str(jsonfilename) + ': ' + str(jsondata))


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