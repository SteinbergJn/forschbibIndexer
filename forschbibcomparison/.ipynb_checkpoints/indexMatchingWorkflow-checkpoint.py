import codecs
import shutil
import sys
import re
import pandas as pd
import time
import xlrd
import unicodecsv
import os
import csv
import config, base

nameFoundFlag = False

def indexMatching(bibsonomyInputFileString, scopusJournalList, sciJournalList, ssciJournalList):
    global nameFoundFlag
    # read mapping file to String
    mappingFileString = readXLSFromDirectoryToString(config.mappingsFileLocation).replace('\r\n', '\n')
    mappingFileStringList = mappingFileString.strip().split('\t')
    soMappingFileStringList = [base.searchOptimize(z) for z in mappingFileStringList]
    print('Mapping file loaded!')
    additionalMappingFileLinesString = ""
    if len(bibsonomyInputFileString) > 3:
        inputString = re.sub('}\n\n@', '}\nJJJJJJJJ\n@', bibsonomyInputFileString)
        bibtexItems = inputString.split("JJJJJJJJ")
        for bibtexItem in bibtexItems:
            bibtexJournalName = ""
            # get id and journal name out of every bibtex item
            for line in bibtexItem.split("\n"):
                if bool(re.search('journal = {', line)):
                    journalName = re.search("{(.+?)}", line)
                    if journalName:
                        bibtexJournalName = journalName.group(1)
            if bool(re.search('\w', bibtexJournalName)) and len(bibtexJournalName) > 2:
                searchTerm = bibtexJournalName
                soSearchTerm = base.searchOptimize(searchTerm)

                if soSearchTerm not in soMappingFileStringList and '""\t""\t""\t""\t""\t"' + bibtexJournalName + '"\n' not in additionalMappingFileLinesString:
                    additionalMappingFileLinesString += '""\t""\t""\t""\t""\t"' + bibtexJournalName + '"\n'

    mappingFileString += additionalMappingFileLinesString

    # print(mappingFileString)
    outputFileString = ""
    soScopusJournalList = [base.searchOptimize(x) for x in scopusJournalList]
    print("Scopus list is optimized!")
    soSciJournalList = [base.searchOptimize(y) for y in sciJournalList]
    print("SCIE list is optimized!")
    soSsciJournalList = [base.searchOptimize(y) for y in ssciJournalList]
    print("SSCI list is optimized!")
    # mappingFileString = re.sub('\t+\n','\n',mappingFileString)
    for line in mappingFileString.split("\n"):
        scopusFlag = False
        scieFlag = False
        ssciFlag = False
        mfsColumns = line.split('\t')
        n = len(mfsColumns)
        for i in range(n):
            if (i > 4):
                soTerm = base.searchOptimize(mfsColumns[i])
                if soTerm in soScopusJournalList:
                    scopusFlag = True
                if soTerm in soSciJournalList:
                    scieFlag = True
                if soTerm in soSsciJournalList:
                    ssciFlag = True
        if scieFlag is True or scopusFlag is True or ssciFlag is True:
            if scopusFlag and "SCOPUSindexed" not in line:
                mfsColumns[1] = "SCOPUSindexed"
            if scieFlag and "SCIEindexed" not in line:
                mfsColumns[2] = "SCIEindexed"
            if ssciFlag and "SSCIindexed" not in line:
                mfsColumns[3] = "SSCIindexed"
            outputLine = '\t'.join(mfsColumns) + '\n'
            outputFileString += outputLine
        else:
            outputFileString += line + '\n'
    # print(outputFileString)
    # move original xlsx file to archive folder
    files = os.listdir(config.mappingsFileLocation)
    for f in files:
        shutil.move(config.mappingsFileLocation + f, './archive/' + re.sub('\W','',str(time.time())) + '.xlsx')
    # save new file in /mappings
    csvStringToXlsx(outputFileString, config.mappingsFileLocation + "journals_index_matches.xlsx")


def readXLSFromDirectoryToString(fileLocation):
    if countFiles(fileLocation) > 1:
        print("There is more than one mapping file in " + fileLocation + "\n\nABBRUCH!")
        sys.exit()
    filename = os.listdir(fileLocation)[0]
    xlsFilepath ="".join([fileLocation, filename])

    tmpFile = xlsFilepath.split('.')[0] + "Temp.csv"
    wb = xlrd.open_workbook(xlsFilepath)
    sh = wb.sheet_by_index(0)
    fh = open(tmpFile, "wb")
    csv_out = unicodecsv.writer(fh, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')

    for row_number in range(sh.nrows):
        csv_out.writerow(sh.row_values(row_number))

    fh.close()
    with codecs.open(tmpFile, 'r', encoding="utf-8") as f:
            return f.read()


def countFiles(in_directory):
    joiner= (in_directory + os.path.sep).__add__
    return sum(
        os.path.isfile(filename)
        for filename
        in map(joiner, os.listdir(in_directory))
    )

def csvStringToXlsx(csvString, outputFilename):
    with codecs.open('./data/csvOutput.tmp', 'w', 'utf-8') as tmp:
        tmp.write(csvString)
    pd.read_csv('./data/csvOutput.tmp', delimiter="\t").to_excel(outputFilename, index=False)

def fillSearchTermArray(term):
    searchTerms=[]
    # remove dotfiles from mapping folder first
    for f in os.listdir(config.mappingsFileLocation):
        if f.startswith('.'):
            os.remove(f)
    mappingsFileString = base.readFileFromDirectoryToString(config.mappingsFileLocation)
    for line in mappingsFileString.splitlines():
        didItMatch = False
        for singleMappingFileEntry in line.split("\t"):
            if len(singleMappingFileEntry) > 2:
                if base.searchOptimize(term) == base.searchOptimize(singleMappingFileEntry):
                    didItMatch = True
        if didItMatch is True:
            for part in line.split("\t"):
                searchTerms.append(part)
    return searchTerms