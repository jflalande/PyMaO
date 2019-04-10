import os
import json



"""
Get a job and launch the missing analyses.
"""
def doJob(queue, xp):
    print("Working")

    while True:
        jsondata = queue.get()
        print("Worker: " + str(jsondata))

        # End of jobs
        if jsondata == "--END--":
            break;

        apkname = next(iter(jsondata))
        jsonanalyses = jsondata[apkname]

        # Looking at each analysis to see if the status is done
        # if not, do the analysis
        for analysis in xp.analyses:
            # print("==========+> " + str(analysis.__dict__))
            analysis_name = analysis.__name__

            if analysis_name in jsonanalyses:
                if jsonanalyses[analysis_name]["status"] != "done":
                    doAnalysis(analysis_name, apkname, jsonanalyses)
            else:
                doAnalysis(analysis_name, apkname, jsonanalyses)

        # Erasing .json file
        writeJson(apkname, xp, jsondata)

"""
Perform an analysis
"""
def doAnalysis(analysis_name, apkname, jsonanalyses):
    print("Worker: ==== perform analysis " + analysis_name + " ====")





    # Finally, writes the JSON file
    jsonanalyses[analysis_name] = {"status" : "done" }


"""Rewrites the JSON file for an apk"""
def writeJson(name, xp, jsondata):
    jsonfilename = os.path.join(xp.JSONBASE, name + ".json")

    if not xp.SIMULATE_JSON_WRITE:
        with open(jsonfilename, 'w') as json_file:
            json.dump(jsondata, json_file)
    else:
        print("Worker: SIMULATION Writing in " + str(jsonfilename) + ': ' + str(jsondata))