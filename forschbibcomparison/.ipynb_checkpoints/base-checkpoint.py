import codecs
import csv
import glob
import logging
import os
import shutil
import tempfile
import urllib.request

import re

import sys

import datetime
import xlrd
import pyquery

import config


def getUserInput():
    return eval('input("--> ")')


# Only one file in directory permitted!!!
def readFileFromDirectoryToString(fileLocation):
    if countFiles(fileLocation) > 1:
        print("There is more than one file in " + fileLocation + "\n\nABBRUCH!")
        sys.exit()
    filename = os.listdir(fileLocation)[0]
    filepath ="".join([fileLocation, filename])
    with codecs.open(filepath, 'r', encoding="utf-8") as f:
            return f.read()


def countFiles(in_directory):
    joiner= (in_directory + os.path.sep).__add__
    return sum(
        os.path.isfile(filename)
        for filename
        in map(joiner, os.listdir(in_directory))
    )






def getScopusJournalList():
    # to get current file via http:
    saveFilePerHttpToDiskAsCsv(config.scopusJournalListUrl, config.scopusFileListFileNameOnDisk)
    # ScopusJournalList = getScopusJournalListOfCsv()


def saveFilePerHttpToDiskAsCsv(url, filename):
    logging.info("Save to file: " + filename + " from " + url)
    print("Save to file: " + filename + " from " + url)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
        # with open(tmp_file.name) as file:
            wb = xlrd.open_workbook(tmp_file.name)
            sh = wb.sheet_by_index(0)
            scopusJournalList = sh.col_values(1, 1)
            your_csv_file = open("./data/" + filename, 'w', encoding='utf8')
            wr = csv.writer(your_csv_file, quoting=csv.QUOTE_ALL)

            for rownum in range(sh.nrows):
                wr.writerow(sh.row_values(rownum))

            your_csv_file.close()
            with codecs.open('./data/' + config.scopusFileListFileNameOnDisk, 'w', 'utf-8') as fw:
                for item in scopusJournalList:
                    fw.write(item + "\n")

def saveFileFromUrlToDisk(url, filename):
    logging.info("Save to file: " + filename + " from " + url)
    print("Save to file: " + filename + " from " + url)
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    pagesString = mybytes.decode("utf-8")
    fp.close()
    with codecs.open('./data/' + filename, 'w', 'utf-8') as fw:
        fw.write(pagesString)



def getScopusJournalList(filename):
    print("./data/" + filename)
    with codecs.open("./data/" + filename, 'r', encoding="utf-8") as f:
        return f.read().splitlines()



def getSciJournalList(filenamePrefix):
    sciList = []
    path = "./data/" + filenamePrefix + "*"
    for filename in glob.glob(path):
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            # print(filename)
            journalNameItems = pyquery.PyQuery(f.read())('body > form > dl > dt')

            for myTag in journalNameItems:
                sciList.append(re.sub('^\d+\. ', '', pyquery.PyQuery(myTag)("strong").text()))
                # print(re.sub('^\d+\. ', '', pyquery.PyQuery(myTag)("strong").text()))
    # print(len(sciList))
    return sciList


def compareJournalEntries(inputString, scopusJournalList, sciJournalList, ssciJournalList, simple):
    lcScopusJournalList = [x.lower() for x in scopusJournalList]
    lcSciJournalList = [y.lower() for y in sciJournalList]
    lcSsciJournalList = [y.lower() for y in sciJournalList]
    soScopusJournalList = [searchOptimize(x) for x in scopusJournalList]
    print("Scopus list is optimized!")
    soSciJournalList = [searchOptimize(y) for y in sciJournalList]
    print("SCIE list is optimized!")
    soSsciJournalList = [searchOptimize(y) for y in ssciJournalList]
    print("SSCI list is optimized!")
    outputDocumentMatches = ""
    outputDocumentNonMatches = ""
    inputString = re.sub('}\n\n@', '}\nJJJJJJJJ\n@', inputString)
    bibtexItems = inputString.split("JJJJJJJJ")
    for bibtexItem in bibtexItems:
        bibtexId = ""
        bibtexJournalName = ""

        # get id and journal name out of every bibtex item
        for line in bibtexItem.split("\n"):
            if line.startswith("@"):
                bibtexId = line
            elif bool(re.search('journal = {', line)):
                journalName = re.search("{(.+?)}", line)
                if journalName:
                    bibtexJournalName = journalName.group(1)
        if bool(re.search('\w', bibtexJournalName)):
            if simple == "simple":
                if bibtexJournalName.lower() in lcScopusJournalList or bibtexJournalName.lower() in lcSciJournalList or bibtexJournalName.lower() in lcSsciJournalList:
                    lineString = bibtexId + "\t" + bibtexJournalName
                    if bibtexJournalName.lower() in lcScopusJournalList:
                        lineString += "\tScopusIndexed"
                    else:
                        lineString += "\t"
                    if bibtexJournalName.lower() in lcSciJournalList:
                        lineString += "\tSCIEIndexed"
                    else:
                        lineString += "\t"
                    if bibtexJournalName.lower() in lcSsciJournalList:
                        lineString += "\tSSCIIndexed"
                    else:
                        lineString += "\t"
                    lineString += "\n"
                    outputDocumentMatches += lineString
                else:
                    outputDocumentNonMatches += bibtexId + "\t" + bibtexJournalName + "\n"
            elif simple =="advanced":
                searchTerm = bibtexJournalName
                # find searchTerm in Mappingtabelle um schreibweisen ins Array zu pushen
                searchTerms = fillSearchTermArray(searchTerm)
                if searchTerms:
                    lineString = ""
                    scopusFlag = False
                    scieFlag = False
                    ssciFlag = False
                    for term in searchTerms:
                        soTerm = searchOptimize(term)
                        if soTerm in soScopusJournalList:
                            scopusFlag = True
                        if soTerm in soSciJournalList:
                            scieFlag = True
                        if soTerm in soSsciJournalList:
                            ssciFlag = True
                    if scieFlag is True or scopusFlag is True or ssciFlag is True:
                        lineString = bibtexId + "\t" + bibtexJournalName
                        if scopusFlag is True: lineString += "\tScopusIndexed"
                        else: lineString += "\t"
                        if scieFlag is True: lineString += "\tSCIEIndexed"
                        else: lineString += "\t"
                        if ssciFlag is True: lineString += "\tSSCIIndexed"
                        else: lineString += "\t"
                        lineString += "\n"
                        outputDocumentMatches += lineString
                    else:
                        outputDocumentNonMatches += bibtexId + "\t" + bibtexJournalName + "\n"
            else:
                print("Parameter für Mapping fehlt!")
                sys.exit()
    now = datetime.datetime.now()

    with codecs.open('./output/' + simple + '_matches' + now.strftime("%Y%m%d_%H%M") + '.csv', 'w', 'utf-8') as fw:
        fw.write(outputDocumentMatches)
    with codecs.open('./output/' + simple + '_nonmatches' + now.strftime("%Y%m%d_%H%M") + '.csv', 'w', 'utf-8') as fw2:
        fw2.write(outputDocumentNonMatches)


def compareJournalEntriesAndPutThemToBibtextFile(inputString, scopusJournalList, sciJournalList, ssciJournalList):
    outputString = ""
    lcScopusJournalList = [x.lower() for x in scopusJournalList]
    lcSciJournalList = [y.lower() for y in sciJournalList]
    lcSsciJournalList = [y.lower() for y in sciJournalList]
    soScopusJournalList = [searchOptimize(x) for x in scopusJournalList]
    print("Scopus list is optimized!")
    soSciJournalList = [searchOptimize(y) for y in sciJournalList]
    print("SCIE list is optimized!")
    soSsciJournalList = [searchOptimize(y) for y in ssciJournalList]
    print("SSCI list is optimized!")
    outputDocumentMatches = ""
    outputDocumentNonMatches = ""
    inputString = re.sub('}\n\n@', '}\nJJJJJJJJ\n@', inputString)
    bibtexItems = inputString.split("JJJJJJJJ")
    for bibtexItem in bibtexItems:
        bibtexId = ""
        bibtexJournalName = ""
        outputItemString = ""
        scopusFlag = False
        scieFlag = False
        ssciFlag = False

        # get id and journal name out of every bibtex item
        for line in bibtexItem.split("\n"):
            outputItemString += line + "\n"
            if bool(re.search('journal = {', line)):
                journalName = re.search("{(.+?)}", line)
                if journalName:
                    bibtexJournalName = journalName.group(1)
        if bool(re.search('\w', bibtexJournalName)) and len(bibtexJournalName) > 3:
            searchTerm = bibtexJournalName
            # find searchTerm in Mappingtabelle um schreibweisen ins Array zu pushen
            searchTerms = fillSearchTermArray(searchTerm)
            if searchTerms:
                for term in searchTerms:
                    soTerm = searchOptimize(term)
                    if soTerm in soScopusJournalList:
                        scopusFlag = True
                    if soTerm in soSciJournalList:
                        scieFlag = True
                    if soTerm in soSsciJournalList:
                        ssciFlag = True
        if scieFlag is True or scopusFlag is True or ssciFlag is True:
            if scopusFlag and "SCOPUSindexed" not in outputItemString:
                outputItemString = re.sub('keywords = {','keywords = {SCOPUSindex ', outputItemString)
            if scieFlag and "SCIEindexed" not in outputItemString:
                outputItemString = re.sub('keywords = {','keywords = {SCIEindex ', outputItemString)
            if ssciFlag and "SSCIindexed" not in outputItemString:
                outputItemString = re.sub('keywords = {','keywords = {SSCIindex ', outputItemString)
            # für jeden gematchten Datensatz ein 'indexproved'
            outputItemString = re.sub('keywords = {','keywords = {indexproved ',outputItemString)
            outputString += outputItemString
            # print(outputItemString)
        else:
            # für jeden _nicht_ gematchten Datensatz ein 'noindex'
            outputItemString = re.sub('keywords = {', 'keywords = {noindex, indexproved ', outputItemString)
            outputString += outputItemString

    now = datetime.datetime.now()

    with codecs.open('./output/enriched_output_' + now.strftime("%Y%m%d_%H%M") + '.bib', 'wb', 'utf-8') as fw:
        fw.write(outputString)



def fillSearchTermArray(term):
    searchTerms=[]
    mappingsFileString = readFileFromDirectoryToString(config.mappingsFileLocation)
    for line in mappingsFileString.splitlines():
        didItMatch = False
        for singleMappingFileEntry in line.split("\t"):
            if len(singleMappingFileEntry) > 2:
                if searchOptimize(term) == searchOptimize(singleMappingFileEntry):
                    didItMatch = True
        if didItMatch is True:
            # searchTerms.append(term)
            for part in line.split("\t"):
                searchTerms.append(part)

    return searchTerms


def searchOptimize(sTerm):
    if type(sTerm) == str:
        if sTerm == "iou": sTerm = "io"
        sTerm = re.sub('"', '', sTerm)
        # strip string
        sTerm = re.sub(' *$', '', sTerm)
        sTerm = re.sub('^ *','', sTerm)
        # Artikel am Anfang des Titels entfernen
        sTerm = re.sub('^Der |^Die |^Das |^The |^Le |^La |^Les |^Los |^A |^An |^Ein |^Eine |^Un |^Une |^El ', '', sTerm)
        # Klammern raus
        sTerm = re.sub(' ?\(.+\)', '', sTerm)
        sTerm = re.sub(' ?\[.+\]', '', sTerm)
        # Untertitel raus
        sTerm = re.sub(' ?:.*$', '', sTerm)
        # &, and, und, et raus
        sTerm = re.sub(' +& +','', sTerm)
        sTerm = re.sub(' +[Aa]nd +| +[Uu]nd +| +[Ee]t +| +UND +| +AND +| +ET +', '', sTerm)
        # ausgeschriebene Umlaute raus
        sTerm = re.sub('ae|ä', 'a', sTerm)
        sTerm = re.sub('oe|ö', 'o', sTerm)
        sTerm = re.sub('ue|ü|Ã¼', 'u', sTerm)
        sTerm = re.sub('ß', 'ss', sTerm)
        sTerm = re.sub('Ae|Ä', 'A', sTerm)
        sTerm = re.sub('Oe|Ö', 'O', sTerm)
        sTerm = re.sub('Ue|Ü', 'U', sTerm)
        # Nicht-Buchstaben raus
        sTerm = re.sub('\W','',sTerm)
        # TEST nicht-ascii raus
        sTerm = re.sub('[^ -~]', '', sTerm)
        # to lower
        sTerm = sTerm.lower()
        # noch mal
        sTerm = re.sub(' *$', '', sTerm)
        sTerm = re.sub('^ *', '', sTerm)


        return sTerm
    else:
        print("no string")
        return None

def checkMappingFileMatches():
    now = datetime.datetime.now()
    soScopusJournalList  = [searchOptimize(x) for x in getScopusJournalList(config.scopusFileListFileNameOnDisk)]
    soScieJournalList    = [searchOptimize(x) for x in getSciJournalList(config.sciFileListNameOnDiskPrefix)]
    soSsciJournalList    = [searchOptimize(x) for x in getSciJournalList(config.ssciFileListNameOnDiskPrefix)]
    mappingsFileString   = readFileFromDirectoryToString(config.mappingsFileLocation)
    outputString         = ""
    # soSsciJournalListString=""
    # soScieJournalListString = ""
    # for item in soSsciJournalList:
    #     soSsciJournalListString += item + "\n"

    # with codecs.open('./output/SSCI_list' + now.strftime("%Y%m%d_%H%M") + '.csv', 'w', 'utf-8') as fw1:
    #     fw1.write(soSsciJournalListString)
    #     fw1.close()

    # for item in soScieJournalList:
    #     soScieJournalListString += item + "\n"

    # with codecs.open('./output/SCIE_list' + now.strftime("%Y%m%d_%H%M") + '.csv', 'w', 'utf-8') as fw2:
    #     fw2.write(soScieJournalListString)
    #     fw2.close()

    # for item in soSsciJournalList:
        # if re.match('kolner', item):
        #    print("ssci: " + item)

    for line in mappingsFileString.splitlines():
        matchScopusflag = False
        matchSCIEFlag   = False
        matchSSCIFlag   = False
        for singleMappingFileEntry in line.split("\t"):
            soTerm = searchOptimize(singleMappingFileEntry)
            # if singleMappingFileEntry.__contains__("Zeitschrift für Soziologie"):
            #    print("Titel: " + singleMappingFileEntry + " - so: " + soTerm)
            if soTerm in soScopusJournalList:
                matchScopusflag = True
            if soTerm in soScieJournalList:
                matchSCIEFlag   = True
            if soTerm in soSsciJournalList:
                matchSSCIFlag   = True

        if matchScopusflag: outputString += "\tScopusMatched"
        else:               outputString += "\t"
        if matchSCIEFlag:   outputString += "\tSCIEMatched"
        else:               outputString += "\t"
        if matchSSCIFlag:   outputString += "\tSSCIMatched"
        else:               outputString += "\t"

        # add journal title to output string
        outputString += "\t" + line + "\n"

    with codecs.open('./output/mappingFile2Indexes_matches' + now.strftime("%Y%m%d_%H%M") + '.csv', 'wb', 'utf-8') as fw:
        fw.write(outputString)
        fw.close()












