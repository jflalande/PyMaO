import os
import time
import datetime
import json
from jsonpath_ng import jsonpath, parse

from os import listdir
from os.path import isfile, join

import BooleanParser

import sys
from pathlib import Path

from collections import Counter # For getting top or botton N

"""
Usage:
    python3 <this_file> <json_config>

where:
    json_config: The file that holds the definitions of the rows and columns to be processed

Example of config file:
    see datasets.json

"""

################################################################################
#                                                                              #
#                       Test zone. Proceed with caution                        #
#                                                                              #
################################################################################

# req = BooleanParser.BooleanParser("$..GetManifAndDexDates.dex_date < 2013")
# print('expression parsed')
# print(req.evaluate({"$..GetManifAndDexDates.dex_date":2012}))

# year_2013 = int(datetime.datetime(2013,1,1,0,0).timestamp())

# check = "$..GetManifAndDexDates.dex_date < 2013"
# poll = "$..ManifestDecoding.minSdkVersion:top:5"
# 
# 
# if len(check.split(":")) > 1:
#     print("The second part is: " + check.split(":")[1])
# else:
#     print("There is no second part, therefore is a bool")
# if len(poll.split(":")) > 1:
#     print("The second part is: " + poll.split(":")[1])
# 
# quit()

################################################################################
#                                                                              #
#                             Function definitions                             #
#                                                                              #
################################################################################


def epoch_to_date(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

os.stat_float_times(False)

def output_json(datasets):
    dico = {}

    for row_name in datasets:
        # print("Assigning row " + row_name)
        row = datasets[row_name]
        dico[row_name] = {}
        for column in row.columns:
            # print("Assiging column " + column.name)
            column.get_total()
            if column.req_type == None:
                dico[row_name][column.name] = [column.total,column.pct_total,column.pct_depend]
            else:
                dico[row_name][column.name] = column.res_poll
    print(str(dico))

def topN(dico,N,poll_type):
    if poll_type == 'top':
        res = dict(Counter(dico).most_common(N))
    elif poll_type == 'bottom':
        res = dict(Counter(dico).most_common()[:N-1:1])
    return res

################################################################################
#                                                                              #
#                          Row and column definition                           #
#                                                                              #
################################################################################

class Column:
    def __init__(self,name,parent_row,req,depend=None):
        self.name = name
        self.total = self.pct_total = self.pct_depend = 0
        self.parent_row = parent_row
        self.req = req 
        self.poll = {}
        self.res_poll = {}
        # print("The req is " + str(self.req))
        # print("The length is " + str(len(self.req.split(":"))))
        if len(self.req.split(":")) < 2:
            self.req_type = None
            self.jpath = self.req.split(" ")[0]
        else:
            # self.req_type can be top or bottom
            self.jpath, self.req_type, self.num_poll = self.req.split(":")
            self.num_poll = int(self.num_poll)
        self.depend = depend
        # print("Column " + self.name  + " created")

    def get_total(self):
        if self.req_type == None:
            if(self.total == 0):
                print("The total is 0, cannot divide by 0")
            else:
                self.pct_total = (self.total / self.parent_row.total)*100
                if self.depend is None:
                    self.pct_depend = self.pct_total
                else:
                    self.pct_depend = (self.total / self.depend.total)*100
        else:
            # print('getting poll')
            self.res_poll = topN(self.poll,self.num_poll,self.req_type)


class Row:
    columns = []

    def __init__(self,name):
        self.name = name
        self.total = 0
        # print("Row " + self.name + " created")

    def create_column(self,name,req,depend_name=None):
        depend = None
        if depend_name != None:
            depend = next((column for column in self.columns if column.name == depend_name), None)        
        # print('this depend is ' + str(depend))
        new_column = Column(name,self,req,depend)
        self.columns.append(new_column)

    def process(self,json_file):
        self.total += 1
        for column in self.columns:
            #print('parsing: ' + str(column.req))
            parse_res = parse(column.jpath).find(mwjson)
            #print("This is the result of the parsing: " + str(parse_res))
            #print()
            if len(parse_res) != 0:
                val = parse_res[0].value
                if column.req_type == None:
                    # print('changing ' + column.jpath + ' -> ' + str(val))
                    req = BooleanParser.BooleanParser(column.req)
                    res = req.evaluate({column.jpath:val})
                    if res:
                        column.total += 1
                else:
                    val = str(val)
                    if val in column.poll.keys():
                        column.poll[val] += 1
                    else:
                        column.poll[val] = 1


################################################################################

################################################################################


print("your arguments are: " + str(sys.argv))

my_file = Path(sys.argv[1])

if not my_file.is_file():
    print("The file doesn't exist. Quitting")
    quit()

filename = sys.argv[1]

with open(filename) as f:
    myjson = json.load(f)

datasets={} # An empty dataset (dictionary)

# for each row # because they are different datasets
for row in myjson['rows']:

#     create row object
    datasets[row] = Row(row)
    # print()

#     create columns
    for column in myjson['columns']:
        # print("the column is " + str(column))
        # create_column(self,name,req,depends=None):
        datasets[row].create_column(column, myjson['columns'][column][0], myjson['columns'][column][1])

    print()
     
#     for each file
    mypath = myjson['rows'][row]
    try:
        files = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    except:
        raise "Cannot open dir"
    
    for filename in files:
        # print("Processing " + filename + " JSON file")
        with open(mypath + "/" + filename) as f:
            mwjson = json.load(f)

        datasets[row].process(mwjson)

output_json(datasets)

quit()

# get config file
# calculate data
# calculate output
