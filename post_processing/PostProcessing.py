import os
import time
import datetime
import json
from jsonpath_ng import jsonpath, parse

from os import listdir
from os.path import isfile, join

import BooleanParser

import sys
# from pathlib import Path

from collections import Counter # For getting top or botton N
from openpyxl import Workbook

"""
Usage:
    python3 <this_file> <json_config>

where:
    json_config: The file that holds the definitions of the rows and columns to be processed

Example of config file:
    see datasets.json

{
    "row":{
        "Dataset 1":"/path/to/dataset/1"
        "Dataset 2":"/path/to/dataset/2"
        "Dataset 3":"/path/to/dataset/3"
    }
    "columns":{
        "Column 1":[
            "<jspath boolean expression>",
            null
        ],
        "Column 2":[
            "<jspath boolean expression>",
            null
        ],
        "Column 3":[
            "<jspath boolean expression>",
            "Column 2"
        ]
    }
}

IDEA:
    Add a dictionary of jsonpath values
    Columns contents for multiexpressions:
        1. The variable boolean expression
        2. A dictionary of variables (the jspath expressions)
        3. The dependency
"""

# Name without extension
outputfilename = "res"

# myjson = {'Drebin': {'date < 2013': [15, 25.862068965517242, 25.862068965517242], 'date > 2012': [43, 74.13793103448276, 74.13793103448276], '15 after 2012': [47, 81.03448275862068, 109.30232558139534], 'Popular SDK Min Version': {'15': 15, '8': 13, '14': 4, '9': 4, '7': 4}}}
#
# print(str(myjson))
#
# with open(outputfilename, 'w') as out:
#     json.dump(myjson, out)
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

def output_to_files(datasets,jsonfile,xlsxfile):
    dico = {}
    row_num = 1

    wb = Workbook()

    # grab the active worksheet
    ws = wb.active

    # Create names for columns in workbook
    for row_name in datasets:
        row = datasets[row_name]
        col_num = 2
        for column in row.columns:
            ws.cell(row=row_num,column=col_num,value=column.name)
            ws.merge_cells(start_row=row_num,start_column=col_num,end_row=row_num,end_column=col_num+1)
            col_num += 2

    row_num += 1
    col_num = 1

    if not os.path.isfile(jsonfile):
        for row_name in datasets:
            # print("Assigning row " + row_name)
            row = datasets[row_name]
            dico[row_name] = {}
            ws.cell(row=row_num,column=col_num,value=row_name)
            col_num += 1
            for column in row.columns:
                # print("Assiging column " + column.name)
                column.get_total()
                if column.req_type == None:
                    dico[row_name][column.name] = [column.total,column.pct_total,column.pct_depend]
                    ws.cell(row=row_num,column=col_num,value=column.total)
                    ws.cell(row=row_num+1,column=col_num,value=column.pct_total)
                    ws.cell(row=row_num+1,column=col_num+1,value=column.pct_depend)
                    # Grand total merge_cells
                    ws.merge_cells(start_row=row_num,start_column=col_num,end_row=row_num,end_column=col_num+1)
                else:
                    dico[row_name][column.name] = column.res_poll
                col_num += 2
            # Dataset name merge
            ws.merge_cells(start_row=row_num,start_column=1,end_row=row_num+1,end_column=1)
            row_num += 2
            col_num = 1
        # print(str(dico))

        print('Creating file at ' + jsonfile)
        with open(jsonfile, 'w') as out:
            json.dump(dico, out)

        # filename = "res.xlsx"
        wb.save(xlsxfile)
        print("File saved at " + xlsxfile)
    else:
        print("file already written. finishing")

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
        # self.req_parser = None
        self.poll = {}
        self.res_poll = {}
        # print("The req is " + str(self.req))
        # print("The length is " + str(len(self.req.split(":"))))
        if len(self.req.split(":")) < 2:
            # Normal request
            self.req_type = None
            self.jpath = self.req.split(" ")[0]
            self.req_parser = BooleanParser.BooleanParser(self.req)
        else:
            # This is poll request, it only needs to retrive a value
            # self.req_type can be top or bottom
            self.jpath, self.req_type, self.num_poll = self.req.split(":")
            self.num_poll = int(self.num_poll)
        self.depend = depend
        # print("Column " + self.name  + " created")

    def get_total(self):
        if self.req_type == None:
            if(self.total == 0):
                print(self.name + ": The total is 0, cannot divide by 0")
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
        self.var_dict = {}
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
            # print('parsing: ' + str(column.name))
            # for var in column.var_list:
            if column.jpath not in self.var_dict.keys():
                self.var_dict[column.jpath] = parse(column.jpath).find(json_file)
            # parse_res = parse(column.jpath).find(json_file)
            #print("This is the result of the parsing: " + str(parse_res))
            #print()
            if len(self.var_dict[column.jpath]) != 0:
                val = self.var_dict[column.jpath][0].value
                if column.req_type == None:
                    # print('changing ' + column.jpath + ' -> ' + str(val))
                    req = column.req_parser
                    res = req.evaluate({column.jpath:val})
                    if res:
                        column.total += 1
                else:
                    val = str(val)
                    if val in column.poll.keys():
                        column.poll[val] += 1
                    else:
                        column.poll[val] = 1
        # Reinitialize
        self.var_dict = {}

################################################################################

################################################################################

def postprocessing(myjsonconfig):

    filename = myjsonconfig

    if not os.path.isfile(filename):
        print("The file doesn't exist. Quitting")
        quit()

    with open(filename) as f:
        myjson = json.load(f)

    jsonfile = myjson['output_dir'] +  "/" + outputfilename + ".json"
    xlsxfile = myjson['output_dir'] +  "/" + outputfilename + ".xlsx"

    if os.path.isfile(jsonfile):
        print("The output file already exist. Quitting")
    else:
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

        output_to_files(datasets,jsonfile,xlsxfile)

def main():
    print("your arguments are: " + str(sys.argv))

    postprocessing(sys.argv[1])

if __name__ == "__main__":
    main()
    quit()
