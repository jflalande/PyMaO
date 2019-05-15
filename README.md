# Experience Orchestrator
## Installation process

```
pip3 install < requirements.txt
sudo apt install openjdk-8-jre-headless
sudo apt install apktool
```

Download the Android SDK, and unzip it in ~/Android/Sdk. Then:

```
cd ~/Android/Sdk/tools
./bin/sdkmanager --update
./bin/sdkmanager "platform-tools"
```

# Usage

- create a new XP in the experiment/ folder
- customize your experiment by being inspired by XPExampleModel.py
- customize run.py

## Post-Processing

Basic usage:
    
    python3 post_processing/PostProcessing.py <json_config_file>


where:

`json_config_file`: The file that holds the definitions of the rows and columns to be processed

For more information about the usge of PostProcessing.py, check the help with:

    python3 post_processing/PostProcessing.py -h

Example of config file:

see `post_processing/examples/drebin.json`

    {
        "rows":{
            "Dataset 1":"/path/to/dataset/1",  ----> Directories that contain JSON
            "Dataset 2":"/path/to/dataset/2",        files generated by the orchestrator
            "Dataset 3":"/path/to/dataset/3",
        },
        "columns":{
            "Column 1":[
                "<boolean expression with JSONPath>",
                null        ---------------------------> No special porcentage is done
            ],
            "Column 2":[
                "<boolean expression with JSONPath>",
                null
            ],
            "Column 3":[
                "<boolean expression with JSONPath>",
                "Column 2"               ------------> Porcentage in relation to Column 2,
            ]                                          which MUST be declared before
        },
        "histograms":{
            "Data 1":[
        			"<JSONPath expression>",
        			"<type>"             ---------------> This can be date only (for the moment)
        		],
        		"Data 2":[
        			"<JSONPath expression>",
        			"<type>"
        		]
        },
        "output_dir":"/path/to/your/output/dir"
    }


The JSONPath implementation is from (https://github.com/h2non/jsonpath-ng)

The boolean expression parser implementation is from (https://gist.github.com/leehsueh/1290686)

It follows this grammar:

    Expression --> Terminal (>,<,>=,<=,==) Terminal
    Terminal --> Number or String or Variable

To compare a variable to a string, they must be enclosed in `""` in the JSON file. For example:

    $..Unzip.status == \"done\"

This expression compares if the variable `$..Unzip.status` is equal to the string `done`.

For our purposes, all the JSONPath expressions are variables.

### TODO:
* [x]  Handle top and bottom surveys
* [ ]  Handle non-dates histograms (little patch)
* [ ]  Expand expression for multiple requests
* [ ]  Add reference in histogram to defined columns